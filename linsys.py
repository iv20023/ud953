# -*- coding: utf-8 -*-
# Author: github.com/madhavajay
"""This is a mathematical Linear System Class"""

from copy import deepcopy
from nonzero import NoNonZeroElements
from plane import Plane


class LinearSystem(object):
    """Creates a linear system of equations for solving"""

    SAME_DIM_MSG = 'All planes in the system should live in the same dimension'
    NO_SOLUTIONS_MSG = 'No solutions'
    INF_SOLUTIONS_MSG = 'Infinitely many solutions'

    def __init__(self, planes):
        try:
            dim = planes[0].dimension
            for plane in planes:
                assert plane.dimension == dim

            self.planes = planes
            self.dimension = dim

        except AssertionError:
            raise Exception(self.SAME_DIM_MSG)

    def swap_rows(self, index_1, index_2):
        """Swap two rows in the linear system to achieve triangular form"""
        row_1 = self.planes[index_1]
        self.planes[index_1] = self.planes[index_2]
        self.planes[index_2] = row_1

    def multiply_coefficient_and_row(self, coefficient, row):
        """Multiply a particular coefficient in a row"""
        plane = self.planes[row]
        plane = plane * coefficient
        self.planes[row] = plane

    def add_multiple_times_row_to_row(self, coefficient, row_to_add,
                                      row_to_be_added_to):
        """Add a multiple of one row to another to help resolve"""

        plane = self.planes[row_to_add]
        plane = plane * coefficient

        self.planes[row_to_be_added_to] += plane

    def get_first_nonzero_indexes(self):
        """Get the indices of the first nonzero term in each row"""
        num_equations = len(self)

        indices = [-1] * num_equations

        for i, plane in enumerate(self.planes):
            try:
                indices[i] = plane.first_nonzero_index(plane.normal_vector)
            except NoNonZeroElements as err:
                if str(err) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                    continue
                else:
                    raise err
        return indices

    def __len__(self):
        return len(self.planes)

    def __getitem__(self, index):
        return self.planes[index]

    def __setitem__(self, index, plane):
        try:
            assert plane.dimension == self.dimension
            self.planes[index] = plane

        except AssertionError:
            raise Exception(self.SAME_DIM_MSG)

    def __str__(self):
        ret = 'Linear System:\n'
        str_format = 'Equation {}: {}'
        temp = [str_format.format(i + 1, p) for i, p in enumerate(self.planes)]
        ret += '\n'.join(temp)
        return ret

    def compute_triangular_form(self):
        """Compute Triangular Form"""
        triangular = deepcopy(self)

        rows = len(triangular.planes)
        dims = triangular.dimension
        dim = 0
        for row in range(0, rows - 1):
            while dim < dims:
                coefficient = triangular.planes[row][dim]
                if coefficient == 0:
                    # we need to swap it for a row we can use to cancel
                    swap = False
                    for next_row in range(row + 1, rows - 1):
                        if triangular.planes[next_row][dim] > 0:
                            triangular.swap_rows(row, next_row)
                            swap = True
                    if swap is False:
                        dim = dim + 1
                else:
                    # we want to use the current row to clear the other others
                    for next_row in range(row + 1, rows):
                        coefficient_remove = triangular.planes[next_row][dim]
                        # negative and positive are valid, is completed already
                        if coefficient_remove != 0:
                            factor = (coefficient_remove / coefficient) * -1
                            reduction_plane = triangular.planes[row] * factor
                            triangular.planes[next_row] = (
                                triangular.planes[next_row] + reduction_plane)
                    # after doing this we need to move to the next row
                    break

        return triangular

    def compute_rref_form(self):
        """Compute RREF Reduced Row Echelon Form"""
        # start at the bottom right, divide by coeffecient to = 1 z term
        # subtract multiple of z term from next one up to clear the z, then
        # divide by the co-efficient
        # finally subtract multiple of z term, then multiple of y term
        # then normalize the coefficient to postive 1

        rref = deepcopy(self.compute_triangular_form())
        rows = len(rref.planes)
        dims = rref.dimension - 1
        dim = dims

        for row in range(rows - 1, -1, -1):
            while dim > -1:
                coefficient = rref.planes[row][dim]
                if coefficient != 0:
                    # go through below coefficients using them to cancel self
                    for range_index in range(row, rows - 1):
                        under_row = range_index + 1

                        # try getting it for cancelling
                        under_coeff = round(rref.planes[under_row][dim], 3)
                        if under_coeff != 0:
                            # use it to cancel the current one
                            # remove the coefficients amount of singular from
                            # the plane below

                            # subtract ratio of below plane to cancel it out
                            positive = coefficient < 0
                            sub_factor = abs(coefficient) / under_coeff

                            reduction_plane = (
                                rref.planes[under_row] * sub_factor)

                            rref.planes[row] = (
                                rref.planes[row] + reduction_plane if positive
                                else rref.planes[row] - reduction_plane)

                # were done with this coefficient so jump to the next dimension
                dim = dim - 1
            # new row so reset the dimension index
            dim = dims

        # finally normalise the coefficients so they are 1 and positive
        rows = len(rref.planes)
        for row in range(rows - 1, -1, -1):
            while dim > -1:
                coefficient = rref.planes[row][dim]
                if coefficient != 0:
                    # then divide by self to get 1 coefficient
                    sub_factor = 1 / coefficient
                    rref.planes[row] = rref.planes[row] * sub_factor
                dim = dim - 1
        return rref
