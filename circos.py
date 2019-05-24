import os
import sys
import argparse
import pandas as pd
from colour import Color
import matplotlib.cm
import matplotlib


INDEX_COL = 1
GENE_COL = 1
COLOR_COL = 1
GENE_COLOR = "100,100,100"


def get_data(filename_data, filename_color, index_col, color_col):
    data = pd.read_table(filename_data, index_col=index_col)
    color = pd.read_table(filename_color, index_col=index_col)
    data["color"] = color.loc[data.index, color.columns[color_col]]
    print(data.head())
    return data


def get_genelist(data, gene_col):
    genelist = list(set([item for sublist in data.iloc[:,gene_col].tolist() for item in sublist.split(",")]))
    print(genelist)
    return genelist


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def get_color(expr, min_logr, max_logr):
    norm = matplotlib.colors.Normalize(vmin=min_logr, vmax=max_logr)
    cmap = matplotlib.cm.get_cmap('hot')
    rgba = cmap(norm(expr))
    return ",".join([str(i) for i in [int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)]])


def get_refactored_data(data, genelist, expression_data, gene_col, color_col=2):
    refactored_data = pd.DataFrame(index=data.index, columns=genelist)
    for gene in genelist:
        for data_index, data_row in data.iterrows():
            if gene in data_row[gene_col]:
                refactored_data.loc[data_index, gene] = 1
    refactored_data.rename(index={item:item.replace(" ", "_").replace("/", "_or_") for item in refactored_data.index}, inplace=True)
    color_list = []


    min_logr = expression_data["LOGR"].min()
    max_logr = expression_data["LOGR"].max()

    for gene in refactored_data.columns:
        gene_color = GENE_COLOR
        try:
            gene_color = get_color(expression_data.loc[gene, "LOGR"], min_logr, max_logr)
        except Exception:
            pass    
        color_list.append(gene_color)
    refactored_data.columns = pd.MultiIndex.from_arrays([color_list, refactored_data.columns], names=["color", "header"])
    refactored_data.reset_index(inplace=True)
    refactored_data.insert(0, data.columns[color_col], data.iloc[:,color_col].tolist())
    return refactored_data


def get_parser():
    parser = argparse.ArgumentParser(description='Parser', add_help=True)
    parser.add_argument("-d", "--data",   help="Path to the data file")
    parser.add_argument("-c", "--color",  help="Path to the color file")
    parser.add_argument("-g", "--gene",  help="Gene expression file")
    parser.add_argument("-o", "--output", help="Path to the output file", default="./output.tsv")
    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args)
    data = get_data(args.data, args.color, INDEX_COL, COLOR_COL)

    expression_data = pd.read_table(args.gene, index_col=0)
    expression_data = expression_data.loc[~expression_data.index.duplicated(keep='first')]

    genelist = get_genelist(data, GENE_COL)
    refactored_data = get_refactored_data(data, genelist, expression_data, GENE_COL)
    refactored_data.to_csv(args.output, sep="\t", na_rep=0, index=False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
