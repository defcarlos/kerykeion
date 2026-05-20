# Kerykeion Feature Enrichments: "Rich Model" Roadmap

This document outlines proposed enhancements for the Vedic features in Kerykeion, moving beyond raw astronomical data to provided interpreted astrological insights.

## 1. Varga Enrichments (Divisional Strength)
**Goal:** Provide immediate context on how a planet performs in a specific divisional chart.

*   **Dignity Status:** Add a `dignity` field to `VargaPointModel`.
    *   Values: `Exalted`, `Moolatrikona`, `Own Sign`, `Great Friend`, `Friend`, `Neutral`, `Enemy`, `Great Enemy`, `Debilitated`.
*   **Vargottama Check:** Add a boolean `is_vargottama` to indicate if a planet is in the same sign as the D1 (Rasi) chart.
*   **Sign Lord:** Explicitly include the `sign_lord` (Traditional Ruler) for each divisional point.
*   **Pushkara Navamsha:** Specifically for D9, indicate if a point falls in a Pushkara (highly auspicious) degree.

## 2. Panchang Enrichments (Interpretive Quality)
**Goal:** Help users understand the "quality of the moment" (Muhurta).

*   **Auspiciousness Status:** Add a `status` field to Tithi, Yoga, and Karana.
    *   Values: `Auspicious`, `Inauspicious`, `Neutral`, `Mixed`.
*   **Core Descriptions:** Add a `meaning` or `description` field for each limb.
    *   *Example:* "Bava Karana: Suitable for creative activities and business growth."
*   **Ruling Planets:** Add a `planetary_ruler` field for each limb.
    *   *Example:* Each Tithi is ruled by a planet (e.g., Pratipada is Sun, Dwitiya is Moon).
*   **Moon Visibility:** Explicitly indicate `is_waxing` (Shukla) or `is_waning` (Krishna) at the top level of the Panchang model.

## 3. Nakshatra Enrichments (Vedic Classifications)
**Goal:** Provide the necessary data for personality analysis and relationship matching (Kootas).

*   **Gana (Nature):** `Deva` (Divine), `Manushya` (Human), `Rakshasa` (Demon).
*   **Yoni (Animal):** The animal archetype (e.g., Horse, Elephant, Serpent) and its gender.
*   **Nadi (Humor):** `Adi` (Vata), `Madhya` (Pitta), `Antya` (Kapha).
*   **Symbolism:** Add a `symbol` text field (e.g., "A Chariot", "A Winnowing Basket").
*   **Tara (Quality):** The Nakshatra's nature (e.g., `Sthira` - Fixed, `Chara` - Movable, `Tikshna` - Sharp).

## 4. Visual & UI Enhancements
*   **Unicode/Emoji Mapping:** Expand the use of emojis for animal signs and symbols.
*   **Color Coding Logic:** Provide suggested "Status Colors" (e.g., Green for Strong, Red for weak) within the model data to assist UI developers.

## Plan: Implementing Advanced Vedic Shadbala Components

1. Sthana Bala: Drekkana Bala
       * Logic: Male planets (Sun, Mars, Jupiter) are strong in the 1st decan (0-10°); Hermaphrodites (Mercury, Saturn) in the 2nd
         (10-20°); Females (Moon, Venus) in the 3rd (20-30°).
       * Implementation: 15 Virupas assigned based on sign-relative longitude.

   2. Kala Bala: Vedic Time Lords
       * Dina Lord (Day): 45 Virupas. The lord of the Vedic day (Sunrise to Sunrise). This requires calculating local sunrise for the
         birth location.
       * Hora Lord (Hour): 60 Virupas. The lord of the planetary hour (1/24th of a day) starting from sunrise.
       * Varsha & Maasa (Year & Month): 15 and 30 Virupas. Calculated via Ahargana (elapsed days from a classical epoch) mapped to the
         360-day Savana year.

   3. Ayana Bala (Equinoctial Strength)
       * Logic: Based on the planet's equatorial declination.
       * Formula: (24 +/- Declination) * 1.25. Planets gain strength based on their northern or southern affinity (e.g., Sun, Mars,
         Jupiter, Venus are Northern-strong).

   4. Yudha Bala (Planetary War)
       * Logic: Applies when Mars, Mercury, Jupiter, Venus, or Saturn are within 1° of conjunction.
       * Calculation: The victor (determined by Raman's disc diameter standards) gains a strength transfer from the loser based on
         their pre-war strength difference.

  Technical Concerns & Caveats

   * Precision vs. Tradition: Swiss Ephemeris provides highly accurate astronomical data (like declination and sunrise), which we will
     use to drive these classical formulas. This creates a "hybrid" approach where traditional math is powered by modern precision.
   * Ayanamsa Dependency: Ayana Bala requires tropical (Sayana) positions. We must ensure that even in sidereal charts, we correctly
     calculate the tropical declination by adding the ayanamsa back to the sidereal positions.
   * Ahargana Epoch: There are several historical epochs for Ahargana. I will use the modern standard (Julian Day based) that most
     accurately reproduces Raman’s year/month lord tables to ensure consistency with standard Vedic software.                   
### Completed Reporting Enhancements

1. **Integrated Shadbala Table:** Standard text reports now include a dedicated section for Shadbala (Six-fold Strength) components.
2. **Dignity Visibility:** Planetary reports now explicitly flag Exalted and Debilitated planets.
3. **Strongest/Weakest Planet Identification:** Examples now demonstrate how to identify the "Lord of the Geniture" based on Shadbala ranking.

# Plan: Vedic SVG Chart Visualizations
## 1. Architectural Philosophy (Pydantic & DRY)
To ensure maximum reusability, we will abstract the chart drawing mechanism into a highly modular, grid-based and geometric system. Currently, `ChartDrawer` is highly optimized for western-style circular wheels. 
**Proposed Architecture:**
*   **Base Models:** Create `VedicChartConfigModel` (Pydantic) to handle shared Vedic visual settings (colors, line weights, font sizes, background styles).
*   **Geometry Engine:** Create a `VedicGeometryUtils` class to handle common SVG paths (e.g., drawing a perfect diamond grid for North Indian, a square grid for South Indian).
*   **Strategy Pattern:** Implement a `BaseVedicDrawer` class. Specific charts (`NorthIndianDrawer`, `SouthIndianDrawer`, `SudarshanaDrawer`) will inherit from this, injecting their specific geometric layouts while reusing the planet-placement logic.

## 2. Proposed Charts & Implementation Mechanics
### A. North Indian Chart (Diamond Style)
*   **Layout:** Fixed houses (1st house is always the top-center diamond). Signs rotate based on the Ascendant.
*   **Logic:** Reuses existing `AstrologicalSubjectModel`. The drawer maps the `house` property of each planet to specific SVG coordinates (the 12 diamonds/triangles).

### B. South Indian Chart (Grid Style)
*   **Layout:** Fixed signs (Aries is always top-left, moving clockwise). Houses rotate based on the Ascendant.
*   **Logic:** Reuses existing models. The drawer maps the `sign` property of each planet to one of the 12 outer squares. The Ascendant is marked with a specific symbol (e.g., "Lg" or a diagonal line).

### C. Sudarshana Chakra (Triple Wheel)
*   **Layout:** Three concentric circular wheels representing the Lagna (Ascendant), Moon, and Sun charts simultaneously.
*   **Logic:** This can heavily reuse the existing circular `ChartDrawer` primitives, but requires a new Pydantic model (`SudarshanaDataModel`) that processes a single subject into three distinct 12-house arrays, aligning them so the 1st house of each respective perspective matches up.

### D. Sarvatobhadra Chakra (9x9 or 10x10 Grid)
*   **Layout:** A complex square grid mapping Nakshatras, Tithis, Weekdays (Vara), Vowels, and Consonants (Aksharas).
*   **Logic:** Highly complex. Used primarily for transits and finding "Vedhas" (obstructions/hits) between transiting planets and natal points (like the first letter of a person's name).

### E. Kalachakra (Wheel of Time)
*   **Layout:** Often depicted as a stylized circle or lotus with 8 petals or spokes, mapping the 28 Nakshatras
         (including Abhijit) and directional lords.
*   **Logic:** Involves complex Dasha/Gati (movement) calculations. Used for predicting major life events based on Navamsha cycles.

## 3. Prerequisite Calculations (Before we start)
Before attempting the complex Chakras (D & E), the following mathematical utilities **must** be developed in Kerykeion:
1.  **Sanskrit Phoneme Mapping (Akshara):** For Sarvatobhadra, we need a utility to map a string (e.g., a person's name) to its corresponding Sanskrit vowel/consonant coordinate on the grid.
2.  **Vedha (Obstruction) Calculator:** Sarvatobhadra requires mathematical logic to calculate diagonal, horizontal, and vertical "lines of sight" across the grid to see which phonemes or nakshatras a transiting planet is "hitting".
3.  **28 Nakshatra System:** Kerykeion currently uses the standard 27 Nakshatra system. Kalachakra and Sarvatobhadra require the 28-Nakshatra system, which includes **Abhijit** (intercalary nakshatra located between Uttarashadha and Shravana).
4.  **Navamsha Gati (Movement) Logic:** For Kalachakra, we need to calculate specific directional jumps (Manduka, Markati, Simhavalokana) based on the Moon's exact Navamsha pada.

## 4. Suggested Additional Vedic Charts
If we are building a comprehensive Vedic visualization suite, these are highly recommended:
*   **Ashtakavarga Grid:** A very common, highly useful tabular grid showing the point distribution (Bindus) for each planet across the 12 signs. We already have the core math for this; we just need a `AshtakavargaDrawer` to render the table.
*   **Chandra / Surya Kundali:** Simple toggles for the North/South drawers to instantly shift the 1st house to the Moon (Chandra) or Sun (Surya) sign.
*   **Nakshatra Chakra (Circular):** A beautiful circular chart explicitly plotting the 27/28 Nakshatras, Padas, and the Navatara (Tara) statuses (Janma, Sampat, Vipat, etc.) relative to the Moon.

## 5. Recommendations: Where to Start
**Phase 1: Foundation (North & South Indian Charts)**
*   **Why:** They are the absolute bedrock of Vedic astrology. They require **zero new calculations**—we have all the planetary, sign, and house data ready.
*   **Goal:** Build the `VedicChartConfigModel`, the base SVGs, and the `NorthIndianDrawer` and `SouthIndianDrawer`.
**Phase 2: Perspective Overlays (Sudarshana & Derivative Kundalis)**
*   **Why:** Leverages existing math. We just need to reorganize the data into the `SudarshanaDataModel` and draw the triple-layered circle.
**Phase 3: Ashtakavarga Visualization**
*   **Why:** Ashtakavarga is arguably more useful for daily predictive astrology than the complex chakras, and the math is much simpler to implement.
**Phase 4: The Complex Chakras (Sarvatobhadra & Kalachakra)**
*   **Why Last:** They require building massive new mathematical sub-systems (28 Nakshatras, Phoneme mapping, Vedha calculation) before a single line of SVG can be drawn.
---
*Created on May 14, 2026*
*Updated on May 15, 2026*