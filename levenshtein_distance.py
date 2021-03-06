# -*- coding: utf-8 -*-
__author__ = 'lufo'

import Queue


class LevenshteinDistance(object):
    """
    a class to compute the Levenshtein distance between two symbol strings
    """

    def __init__(self, templates, string_or_list=0):
        """
        :param templates: a list include template strings
        :param string_or_list: 0:compare between strings
                               1:compare between lists
        """
        self.T = 20
        self.threshold = self.T
        self.templates_length_list = []
        self.templates = templates
        self.begin_distance = []
        self.temp_templates_added_length_list = []
        self.template = '' if string_or_list == 0 else []
        for i in xrange(0, len(self.templates)):
            if string_or_list == 0:
                self.templates[i] = ' ' + self.templates[i]
                self.template += self.templates[i]
            else:
                self.templates[i] = [' '] + self.templates[i]
                self.template.extend(self.templates[i])
            self.templates_length_list.append(len(self.templates[i]))
            if i == 0:
                self.temp_templates_added_length_list.append(len(self.templates[i]))
            else:
                self.temp_templates_added_length_list.append(
                    len(self.templates[i]) + self.temp_templates_added_length_list[i - 1])
        self.temp_templates_added_length_list.append(0)
        self.distance_matrix_rows = len(self.template)
        self.templates_added_length_list = [0 for i in xrange(0, self.distance_matrix_rows + 1)]
        for i in self.temp_templates_added_length_list:
            self.templates_added_length_list[i] = 1
        self.temp_distance = [float('inf') for i in xrange(0, self.distance_matrix_rows)]
        for i in xrange(0, len(self.templates_length_list)):
            self.begin_distance.extend([i for i in xrange(0, self.templates_length_list[i])])
        self.old_extensible_index = [1 for i in xrange(0, self.distance_matrix_rows)]


    def levenshtein_distance(self, input_string, strategy, case_sensitive=0, string_or_list=0, lexical_tree=0,
                             transform_list_in=[], transform_list_out=[], begin_distance=[], segment=0):
        """
        a routine to compute the Levenshtein distance between strings
        :param input_string: the input_string string
        :param strategy: 0:based on a maximum string edit distance of 3
                         1:based on a "beam" of 3 relative to the current best score in any column of the trellis
        :param case_sensitive: 0:don't case sensitive
                               1:case sensitive
        :param string_or_list: 0:compare between strings
                               1:compare between lists
        :param lexical_tree: 1:use lexical tree as template
        :param transform_list: a list,each element is a dict represent a node in this lexical tree,
        this dict's key is the root node of the tree,and it's value is a list include position of this tree's parent nodes
        :param segment: 1 if use this function to segment, else 0
        :return: min_distance: minimum distance between input string and multiple templates
        :param begin_distance: a list, ith element is the ith nodes begin cost in lexical tree
        :return: template: template that has minimum distance
        :return: path: path from end to begin
        """
        if string_or_list == 0:
            input_string = ' ' + input_string  # to avoid the bug when compare 'this' with 'his'
        else:
            input_string = [' '] + input_string
        column = self.template
        row = input_string
        distance_matrix_columns = len(row)
        distance = begin_distance if lexical_tree else self.begin_distance[:]
        old_extensible_index = self.old_extensible_index[:]
        last_block_position = [[0 for i in xrange(self.distance_matrix_rows)] for j in
                               xrange(distance_matrix_columns)]
        for i in xrange(1, distance_matrix_columns):
            new_extensible_index = [0 for j in xrange(0, self.distance_matrix_rows)]
            new_distance = self.temp_distance[:]
            for j in xrange(0, self.distance_matrix_rows):
                if old_extensible_index[j]:
                    if self.templates_added_length_list[j]:
                        new_distance[j] = i
                    else:
                        cost = 0 if self.equal(column[j], row[i], case_sensitive) else 1
                        if lexical_tree:
                            parent_node_index = transform_list_in[j].values()[0][0]
                        else:
                            parent_node_index = j - 1
                        new_distance[j] = min(distance[j] + 1, distance[parent_node_index] + cost,
                                              new_distance[parent_node_index] + 1)
                        index = [distance[j] + 1, distance[parent_node_index] + cost,
                                 new_distance[parent_node_index] + 1].index(
                            new_distance[j])
                        if index == 0:
                            last_block_position[i][j] = [i - 1, j]
                        elif index == 1:
                            last_block_position[i][j] = [i - 1, parent_node_index]
                        else:
                            last_block_position[i][j] = [i, parent_node_index]
            if segment:
                for j, list in enumerate(transform_list_out):
                    if not list.values()[0]:
                        if new_distance[0] > new_distance[j]:
                            new_distance[0] = new_distance[j]
                            last_block_position[i][0] = [i, j]
            self.threshold = self.T if strategy == 0 else min(new_distance) + self.T
            for j in xrange(0, self.distance_matrix_rows):
                new_extensible_index[j] = 1
                if new_distance[j] <= self.threshold:
                    if lexical_tree:
                        for subnode_index in transform_list_out[j].values()[0]:
                            new_extensible_index[subnode_index] = 1
                    else:
                        if not self.templates_added_length_list[j + 1]:
                            new_extensible_index[j + 1] = 1
            old_extensible_index = new_extensible_index[:]
            # print distance
            distance = new_distance[:]
        # print distance
        if lexical_tree:
            min_distance = float('inf')
            j = 0
            for i, cur_distance in enumerate(distance):
                if cur_distance < min_distance and (len(transform_list_out[i].values()[0]) == 0):
                    min_distance = cur_distance
                    j = i
            best_template = self.template[j]
            last_index = j
        else:
            total_distance = [distance[i - 1] for i in self.temp_templates_added_length_list[:-1]]
            min_distance = min(total_distance)
            j = self.temp_templates_added_length_list[total_distance.index(min_distance)] - 1
        i = distance_matrix_columns - 1
        path = []
        while last_block_position[i][j] != 0:
            last_position = last_block_position[i][j][:]
            path.append(last_position)
            i = last_position[0]
            j = last_position[1]
        if lexical_tree:
            for position in path:
                if position[1] != last_index:
                    best_template += self.template[position[1]]
                    last_index = position[1]
            best_template = best_template[::-1]
        else:
            best_template = self.templates[total_distance.index(min_distance)]
        return min_distance, best_template.lower() if string_or_list == 0 else best_template, path


    def equal(self, char1, char2, case_sensitive):
        """
        compare whether two chars are the same
        :param char1: first char
        :param char2: second char
        :param case_sensitive: 0:don't case sensitive
                               1:case sensitive
        :return: self.True if char1 equal char2,False otherwise
        """
        if case_sensitive:
            return char1 == char2
        else:
            return char1.lower() == char2.lower()


def levenshtein_distance_using_lexical_tree(lexical_tree, input_string, strategy=0, case_sensitive=0):
    """
    a routine to compute the Levenshtein distance between strings using lexical tree as template
    :param lexical_tree: a dict, re
    :param input_string:
    :param strategy:
    :param case_sensitive:
    :return:
    """