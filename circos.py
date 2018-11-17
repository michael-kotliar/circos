import os
import sys
import argparse
import pandas as pd


INDEX_COL = 2
TARGET_COL = 7
GENE_COL = 9
COLOR_COL = 10


def get_data(filename, index_col):
    return pd.read_table(filename, index_col=index_col)


def get_genelist(data, gene_col):
    return list(set([item for sublist in data.iloc[:,gene_col].tolist() for item in sublist.split(",")]))


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def get_refactored_data(data, genelist, target_col, gene_col, color_col):
    refactored_data = pd.DataFrame(index=data.index, columns=genelist)
    for gene in genelist:
        for data_index, data_row in data.iterrows():
            if gene in data_row[gene_col]:
                refactored_data.loc[data_index, gene] = data_row[target_col]
    refactored_data.rename(index={item:item.replace(" ", "_").replace("/", "_or_") for item in refactored_data.index}, inplace=True)
    refactored_data.reset_index(inplace=True)
    refactored_data.insert(0, data.columns[COLOR_COL], data.iloc[:,COLOR_COL].tolist())
    return refactored_data


def get_parser():
    parser = argparse.ArgumentParser(description='Parser', add_help=True)
    parser.add_argument("-d", "--data", help="Path to the data file")
    parser.add_argument("-o", "--output", help="Path to the output file", default="./output.tsv")
    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args)
    data = get_data(args.data, INDEX_COL)
    genelist = get_genelist(data, GENE_COL)
    refactored_data = get_refactored_data(data, genelist, TARGET_COL, GENE_COL, COLOR_COL)
    refactored_data.to_csv(args.output, sep="\t", na_rep=0, index=False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
