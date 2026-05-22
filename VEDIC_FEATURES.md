# Kerykeion: Vedic (Jyotish) & Hybrid Features Guide

This document outlines the Indian astrological features implemented in Kerykeion. The library now supports a "Paradigm-Decoupled" architecture, allowing users to calculate charts in any zodiac (Tropical or Sidereal) and interpret them through either Western or Vedic lenses.

---

## 1. The Hybrid Paradigm Architecture

Kerykeion distinguishes between **Astronomy** (degrees/zodiac) and **Astrology** (interpretation rules). This enables the "Tropical Vedic" workflow.

### Toggling Paradigms
The `ReportGenerator` and core data models now support a `paradigm` toggle.

```python
from kerykeion import AstrologicalSubjectFactory, ReportGenerator

# Calculate in Tropical Zodiac
subject = AstrologicalSubjectFactory.from_birth_data("User", 1990, 1, 1, 12, 0, "London", "GB")

# Case A: Interpret as Western (Default)
# Shows Ptolemaic aspects, modern rulers, and Western dignity labels.
report_w = ReportGenerator(subject, paradigm="Western")

# Case B: Interpret as Vedic (Tropical Vedic)
# Shows Graha Drishti, traditional rulers, and Parashari dignity labels.
report_v = ReportGenerator(subject, paradigm="Vedic")
```

---

## 2. Graha Drishti (Planetary Aspects)

Unlike Western aspects based on degree orbs, Vedic aspects are **sign-based** "glances."

### The Drishti Engine (`kerykeion.aspects.vedic_aspects`)
- **All Planets:** Aspect the 7th sign from their position.
- **Mars:** Special aspects on 4th and 8th signs.
- **Jupiter:** Special aspects on 5th and 9th signs.
- **Saturn:** Special aspects on 3rd and 10th signs.

**Code Example:**
```python
from kerykeion.aspects.vedic_aspects import get_graha_drishti

drishti_list = get_graha_drishti(subject)
for d in drishti_list:
    print(f"{d.p1_name} casts {d.aspect} on {d.p2_name}")
```

---

## 3. Exhaustive Shadbala Diagnostics

Shadbala is a six-fold planetary strength model. Kerykeion provides a deep "X-ray" view into these scores.

### Key Components Exposed:
1.  **Sthana Bala:** Ucha (Exaltation), Saptavarga (Divisional), Kendradi (Angular), etc.
2.  **Dig Bala:** Directional strength based on house distance.
3.  **Kala Bala:** Temporal strength (Day/Night, Moon Phase, Timelords).
4.  **Chesta Bala:** Motional strength based on relative speed and retrogression.
5.  **Naisargika Bala:** Inherent natural luminosity.
6.  **Drik Bala:** Net aspectual support (Benefic support vs. Malefic obstacles).
7.  **Yudha Bala:** Adjustments for planets in "War" (conjunction within 1°).

**Code Example:**
```python
# Access raw sub-metrics
sun_sb = subject.shadbala.sun
print(f"Sun Net Support (Drik): {sun_sb.drik_bala}")
print(f"Sun Speed Ratio: {sun_sb.chesta_ratio}")

# In Reports
ReportGenerator(subject).print_report(show_shadbala_details=True)
```

---

## 4. Nakshatras (Lunar Mansions)

One of the most powerful features of Kerykeion is the deep integration of the 27 Nakshatras. Unlike many libraries that only calculate the Nakshatra for the Moon, Kerykeion applies this logic to **every celestial point**.

### The "Nakshatra Ayanamsa" (Hybrid Calculation)
Kerykeion allows for a sophisticated hybrid approach: you can calculate the main chart in the **Tropical** zodiac but calculate Nakshatras using a **Sidereal** Ayanamsa (like Lahiri). This is the standard for "Tropical Vedic" practitioners.

```python
# Main Zodiac is Tropical, but Nakshatras use Lahiri Ayanamsa
subject = AstrologicalSubjectFactory.from_birth_data(
    ...,
    zodiac_type="Tropical",
    nakshatra_ayanamsa="LAHIRI" 
)
```

### Deep Metadata for Every Point
Each `KerykeionPointModel` (e.g., `subject.sun`, `subject.mars`) now carries the following Vedic classifications:
- **Nakshatra:** The name (e.g., "Rohini").
- **Pada:** The quarter (1-4).
- **Lord:** The Vimsottari Dasha lord (e.g., "Moon").
- **Deity:** The ruling divinity (e.g., "Brahma").
- **Gana:** Nature (Deva, Manushya, Rakshasa).
- **Yoni:** Animal archetype (e.g., "Serpent").
- **Nadi:** Humor (e.g., "Kapha").
- **Quality:** Fixed, Sharp, Swift, etc.

---

## 5. Panchang (The Five Limbs of Time)

The `panchang` attribute on `AstrologicalSubject` provides the Vedic time-keeping essentials:
- **Tithi:** Lunar Day (with Status, Deity, and Start/End times).
- **Vara:** Vedic Weekday (measured from Sunrise to Sunrise).
- **Nakshatra:** Lunar Mansion (of the Moon).
- **Yoga:** Soli-lunar relationship.
- **Karana:** Half-Tithi.

---

## 6. Vimsottari Dasha Engine (Predictive Timing)

Kerykeion implements a full-lifecycle Vimsottari Dasha system, calculating the nested planetary cycles that dictate timing in Vedic astrology.

### Features:
- **Hierarchical Calculation:** Supports Mahadasha (major), Antardasha (minor), and Pratyantardasha (sub-minor) levels.
- **Precision Timing:** Uses Julian Day arithmetic for exact period boundaries, avoiding Gregorian drift.
- **Auto-Reference:** The `ReportGenerator` automatically identifies the active period for the subject's birth or current time.

**Code Example:**
```python
subject = AstrologicalSubjectFactory.from_birth_data(...)

# Access the first Mahadasha (the birth lord)
first_md = subject.dasha.mahadashas[0]
print(f"Birth Mahadasha: {first_md.lord} until {first_md.end_date}")

# Access Antardashas within that Mahadasha
for ad in first_md.antardashas:
    print(f"  Antardasha: {ad.lord} starts at {ad.start_date}")
```

---

## 7. Divisional Charts (Vargas)

Vedic astrology uses divisional charts to see specific areas of life. Kerykeion calculates the **Saptavarga** (7 main divisions):
- **D1 (Rasi):** Main chart.
- **D9 (Navamsha):** Fruits of life/Dharma (Crucial for strength).
- **D2 (Hora), D3 (Drekkana), D7 (Saptamsha), D12 (Dwadasamsha), D30 (Trimsamsha).**

### Varga Enrichments:
- **Vargottama:** True if a planet is in the same sign in D1 and D9.
- **Pushkara Navamsha:** Highly auspicious degrees within divisional signs.
- **Traditional Rulers:** sign_lord field uses strictly 7-planet traditional rulership.

---

## 8. Tattvas, Gunas, and Rulerships

The library automatically renames and recalculates core classifications when the Vedic paradigm is active:

| Western Term | Vedic Equivalent |
| :--- | :--- |
| **Elements** | **Tattvas** (Agni, Prithvi, Vayu, Jala) |
| **Qualities** | **Gunas** (Rajas, Tamas, Sattva) |
| **Rulers** | Strictly **Traditional** (e.g., Aquarius = Saturn) |

---

## 9. Utilities & Helpers

- `vedic_utils.get_vedic_dignity()`: Sign-based dignity (Exalted, Friend, Neutral, Enemy, etc.).
- `nakshatra_utils.get_nakshatra_data()`: Full classification (Gana, Yoni, Nadi, Quality).
- `panchang_utils.get_sunrise_sunset()`: Accurate calculation of Vedic day boundaries.
- `western_utils.get_western_dignity()`: Ptolemaic dignity (Domicile, Detriment, Fall).

### Important Note on House Systems
While Kerykeion supports many house systems (Placidus, Koch, etc.), the **Vedic Paradigm** is designed to work with **Whole Sign Houses (`'W'`)**. Using other systems may result in interpretative inaccuracies regarding Drishti and Yogas.
