# -*- coding: utf-8 -*-
"""
Vedic Geometry Utilities
"""

class VedicGeometryUtils:
    """
    Utility class for generating SVG paths for Vedic charts.
    """

    @staticmethod
    def get_north_indian_grid_paths(width: float, height: float, padding: float = 0) -> list[str]:
        """
        Generates SVG path strings for the North Indian diamond-style grid.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        x1, y1 = padding + w, padding + h
        xm, ym = padding + w / 2, padding + h / 2

        paths = []
        # Outer border
        paths.append(f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z")
        # Diagonals
        paths.append(f"M {x0} {y0} L {x1} {y1}")
        paths.append(f"M {x0} {y1} L {x1} {y0}")
        # Inner diamond
        paths.append(f"M {xm} {y0} L {x1} {ym} L {xm} {y1} L {x0} {ym} Z")

        return paths

    @staticmethod
    def get_south_indian_grid_paths(width: float, height: float, padding: float = 0) -> list[str]:
        """
        Generates SVG path strings for the South Indian square-style grid.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding

        paths = []
        # Outer border
        paths.append(f"M {x0} {y0} L {x0 + w} {y0} L {x0 + w} {y0 + h} L {x0} {y0 + h} Z")

        # Grid lines (4x4)
        for i in range(1, 4):
            # Vertical
            vx = x0 + i * (w / 4)
            paths.append(f"M {vx} {y0} L {vx} {y0 + h}")
            # Horizontal
            hy = y0 + i * (h / 4)
            paths.append(f"M {x0} {hy} L {x0 + w} {hy}")

        return paths

    @staticmethod
    def get_north_indian_house_centers(width: float, height: float, padding: float = 0) -> list[tuple[float, float]]:
        """
        Returns the center coordinates for the 12 houses in a North Indian chart.
        House 1 is top-center.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        xm, ym = x0 + w / 2, y0 + h / 2

        # Approximate centers for the 12 triangles/diamonds
        # 1st house (top diamond)
        h1 = (xm, y0 + h / 4)
        # 2nd house (top-left triangle)
        h2 = (x0 + w / 4, y0 + h / 8)
        # 3rd house (left-top triangle)
        h3 = (x0 + w / 8, y0 + h / 4)
        # 4th house (left diamond)
        h4 = (x0 + w / 4, ym)
        # 5th house (left-bottom triangle)
        h5 = (x0 + w / 8, y0 + 3 * h / 4)
        # 6th house (bottom-left triangle)
        h6 = (x0 + w / 4, y0 + 7 * h / 8)
        # 7th house (bottom diamond)
        h7 = (xm, y0 + 3 * h / 4)
        # 8th house (bottom-right triangle)
        h8 = (x0 + 3 * w / 4, y0 + 7 * h / 8)
        # 9th house (right-bottom triangle)
        h9 = (x0 + 7 * w / 8, y0 + 3 * h / 4)
        # 10th house (right diamond)
        h10 = (x0 + 3 * w / 4, ym)
        # 11th house (right-top triangle)
        h11 = (x0 + 7 * w / 8, y0 + h / 4)
        # 12th house (top-right triangle)
        h12 = (x0 + 3 * w / 4, y0 + h / 8)

        return [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12]

    @staticmethod
    def get_south_indian_sign_centers(width: float, height: float, padding: float = 0) -> list[tuple[float, float]]:
        """
        Returns the center coordinates for the 12 signs in a South Indian chart.
        Signs are fixed: Aries is top-row, second-from-left (or top-left depending on tradition,
        usually it's:
        11 12 01 02 (Pisces, Aries, Taurus, Gemini) - top row
        10       03
        09       04
        08 07 06 05
        Wait, standard South Indian is:
        Pisc Ari Tau Gem
        Aqu       Can
        Cap       Leo
        Sag Sco Lib Vir

        Actually:
        [1,0] Ari, [2,0] Tau, [3,0] Gem, [3,1] Can, [3,2] Leo, [3,3] Vir, [2,3] Lib, [1,3] Sco, [0,3] Sag, [0,2] Cap, [0,1] Aqu, [0,0] Pis
        indices (col, row):
        (1,0), (2,0), (3,0), (3,1), (3,2), (3,3), (2,3), (1,3), (0,3), (0,2), (0,1), (0,0)
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        cw, ch = w / 4, h / 4

        # Centers for cells (col, row)
        def get_center(col, row):
            return (x0 + (col + 0.5) * cw, y0 + (row + 0.5) * ch)

        # Signs 1-12 (Aries to Pisces)
        aries = get_center(1, 0)
        taurus = get_center(2, 0)
        gemini = get_center(3, 0)
        cancer = get_center(3, 1)
        leo = get_center(3, 2)
        virgo = get_center(3, 3)
        libra = get_center(2, 3)
        scorpio = get_center(1, 3)
        sagittarius = get_center(0, 3)
        capricorn = get_center(0, 2)
        aquarius = get_center(0, 1)
        pisces = get_center(0, 0)

        return [aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces]
