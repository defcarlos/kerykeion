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
        The center 2x2 area is a single square.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        x1, y1 = x0 + w, y0 + h

        cw, ch = w / 4, h / 4

        paths = []
        # Outer border
        paths.append(f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z")

        # Vertical lines
        # Left internal
        paths.append(f"M {x0 + cw} {y0} L {x0 + cw} {y1}")
        # Middle internal (only top and bottom)
        paths.append(f"M {x0 + 2*cw} {y0} L {x0 + 2*cw} {y0 + ch}")
        paths.append(f"M {x0 + 2*cw} {y1 - ch} L {x0 + 2*cw} {y1}")
        # Right internal
        paths.append(f"M {x0 + 3*cw} {y0} L {x0 + 3*cw} {y1}")

        # Horizontal lines
        # Top internal
        paths.append(f"M {x0} {y0 + ch} L {x1} {y0 + ch}")
        # Middle internal (only left and right)
        paths.append(f"M {x0} {y0 + 2*ch} L {x0 + cw} {y0 + 2*ch}")
        paths.append(f"M {x1 - cw} {y0 + 2*ch} L {x1} {y0 + 2*ch}")
        # Bottom internal
        paths.append(f"M {x0} {y0 + 3*ch} L {x1} {y0 + 3*ch}")

        return paths
    @staticmethod
    def get_north_indian_house_polygons(width: float, height: float, padding: float = 0) -> list[list[tuple[float, float]]]:
        """
        Returns the polygon points for each of the 12 houses in a North Indian chart.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        x1, y1 = x0 + w, y0 + h
        xm, ym = x0 + w / 2, y0 + h / 2
        
        # Intersections of diagonals and diamond
        # M1 (top-left), M2 (bottom-left), M3 (bottom-right), M4 (top-right)
        m1 = (x0 + w / 4, y0 + h / 4)
        m2 = (x0 + w / 4, y0 + 3 * h / 4)
        m3 = (x0 + 3 * w / 4, y0 + 3 * h / 4)
        m4 = (x0 + 3 * w / 4, y0 + h / 4)
        
        # Nodes
        a, b, c = (x0, y0), (xm, y0), (x1, y0)
        d, e, f = (x0, ym), (xm, ym), (x1, ym)
        g, h, i = (x0, y1), (xm, y1), (x1, y1)
        
        # 12 Houses
        return [
            [b, e, d],      # H1
            [a, b, m1],     # H2
            [a, d, m1],     # H3
            [d, e, h],      # H4
            [g, d, m2],     # H5
            [g, h, m2],     # H6
            [h, e, f],      # H7
            [i, h, m3],     # H8
            [i, f, m3],     # H9
            [f, e, b],      # H10
            [c, f, m4],     # H11
            [c, b, m4]      # H12
        ]

    @staticmethod
    def get_south_indian_sign_polygons(width: float, height: float, padding: float = 0) -> list[list[tuple[float, float]]]:
        """
        Returns the polygon points for each of the 12 sign boxes in a South Indian chart.
        """
        w = width - 2 * padding
        h = height - 2 * padding
        x0, y0 = padding, padding
        cw, ch = w / 4, h / 4
        
        def get_box(col, row):
            bx0, by0 = x0 + col * cw, y0 + row * ch
            bx1, by1 = bx0 + cw, by0 + ch
            return [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
            
        # Signs 1-12 (Aries to Pisces)
        return [
            get_box(1, 0), get_box(2, 0), get_box(3, 0), # Ari, Tau, Gem
            get_box(3, 1), get_box(3, 2), get_box(3, 3), # Can, Leo, Vir
            get_box(2, 3), get_box(1, 3), get_box(0, 3), # Lib, Sco, Sag
            get_box(0, 2), get_box(0, 1), get_box(0, 0)  # Cap, Aqu, Pis
        ]

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
