#!/usr/bin/env python3

"""Validate SC2 & SC3."""

import argparse
import json

import dendropy


def valid_leaf_names(tree, gs_tree):
    """Check that prediction tree uses correct leaf labels."""

    gs_leaves = {t.label for t in gs_tree.taxon_namespace}

    root_taxon_exists = tree.find_node_with_taxon_label('root')
    if root_taxon_exists:
        gs_leaves.add('root')

    submission_leaves = set([t.label for t in tree.taxon_namespace])
    intersect = gs_leaves.intersection(submission_leaves)
    valid = len(intersect) == len(gs_leaves)

    return valid


def validate_tree(pred_tree, gs_tree):
    """Validate submission tree

    Args:
        pred_tree: Submission tree
        gs_tree: Goldstandard tree

    Returns:
        list of invalid reasons
    """
    invalid_errors = []
    root_node_exists = pred_tree.find_node_with_label('root')
    root_taxon_exists = pred_tree.find_node_with_taxon_label('root')
    if not root_node_exists and not root_taxon_exists:
        invalid_errors.append("Prediction tree must contain 'root' node")
    elif root_node_exists and root_taxon_exists:
        invalid_errors.append("Prediction tree must have a single 'root' node")
    else:
        if not valid_leaf_names(pred_tree, gs_tree):
            invalid_errors.append(f"Prediction tree must use the correct identifier"
                                  f" names, and contain {len(gs_tree.taxon_namespace):,}"
                                  " cell lines.")
    return invalid_errors


def main(submission, entity_type, goldstandard, results):
    """Validate submission and write results to JSON.

    Args:
        submission: input file
        entity: Synapse entity type
        results: output file
    """

    invalid_reasons = []
    gs_tree = dendropy.Tree.get(file=open(goldstandard, 'r'),
                                schema="newick",
                                tree_offset=0)
    if submission is None:
        invalid_reasons = [
            f"Expected FileEntity type but found {entity_type}"]
    else:
        try:
            pred_tree = dendropy.Tree.get(file=open(submission, 'r'),
                                          schema="newick",
                                          tree_offset=0)
        except Exception as err:
            invalid_reasons = [
                f"Prediction tree not a valid Newick tree format: {err}"]
        else:
            invalid_reasons.extend(validate_tree(pred_tree, gs_tree))

    prediction_file_status = "INVALID" if invalid_reasons else "VALIDATED"

    result_dict = {'prediction_file_errors': "\n".join(invalid_reasons)[:500],
                   'prediction_file_status': prediction_file_status,
                   'round': 1}

    with open(results, 'w') as out:
        out.write(json.dumps(result_dict))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--submission_file",
                        help="Submission file")
    parser.add_argument("-g", "--goldstandard",
                        required=True, help="Truth file")
    parser.add_argument("-e", "--entity_type",
                        required=True, help="Synapse entity type")
    parser.add_argument("-r", "--results",
                        required=True, help="Results file")

    args = parser.parse_args()
    if not args.submission_file:
        with open(args.results, 'w') as out:
            out.write(json.dumps(
                {'prediction_file_errors':
                    "Submission must be a Synapse File, not Folder/Project",
                 'prediction_file_status': "INVALID",
                 'round': 1}
            ))
    else:
        main(args.submission_file, args.entity_type,
             args.goldstandard, args.results)
