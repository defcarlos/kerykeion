# Kerykeion Vedic Feature Roadmap

This document tracks the evolution of Kerykeion's Vedic (Jyotish) capabilities, distinguishing between completed architectural enhancements and upcoming predictive features.

---

## ✅ Completed Features

### 1. Hybrid Tradition Engine (Architectural Foundation)
*   **Paradigm Decoupling:** Complete separation of astronomical calculations (Zodiac/Degrees) from interpretative logic (Western vs. Vedic).
*   **Dual Calculation:** Concurrent calculation of both Western (Ptolemaic) and Vedic (Parashari) dignities, aspects, and classifications.
*   **Sign-Based Aspects (Drishti):** Implementation of the sign-counting "glance" system including special aspects for Mars, Jupiter, and Saturn.

### 2. Rich Vedic Data Models
*   **Varga Enrichments:** Standard support for Saptavarga (D1, D2, D3, D7, D9, D12, D30) with dignity, vargottama, and pushkara status.
*   **Exhaustive Shadbala:** Full breakdown of the 6 major balas and their 13+ nested sub-metrics (Ucha, Saptavarga, Chesta ratio, etc.).
*   **Panchang Limb Data:** Interpretation and status for Tithi, Vara, Yoga, Karana, and Nakshatra.
*   **Nakshatra Classifications:** Full metadata for every celestial point (Gana, Yoni, Nadi, Lord, Deity).

### 3. Vedic Visualizations (SVG)
*   **North Indian Chart:** Diamond-style grid with fixed houses and rotating signs.
*   **South Indian Chart:** Square-style grid with fixed signs and rotating houses.
*   **Sudarshana Chakra:** Triple-concentric wheel aligning Lagna, Chandra, and Surya perspectives.

---

## 🚀 Planned Features (Upcoming)

### 1. Vimsottari Dasha Engine (Predictive Timing)
*   **Goal:** Calculate the major (Mahadasha), minor (Antardasha), and sub-minor (Pratyantardasha) planetary cycles based on the Moon's Nakshatra degree.
*   **Extensions:** Support for other dasha systems like Yogini Dasha and Chara Dasha.

### 2. Ashtakavarga Engine (Point-Based Strength)
*   **Goal:** Implement the numerical point system (Bindus) for each planet across the 12 signs.
*   **Output:** Calculation of the Bhinnashtakavarga (Individual) and Sarvashtakavarga (Total) tables to provide transit suitability scores.

### 3. Advanced Varga Expansion
*   **Goal:** Move beyond Saptavarga to include the Shodasavarga (16 divisional charts).
*   **Focus:** D10 (Dasamsha - Career), D16 (Shodashamsha - Vehicles), D24 (Chaturvimshamsha - Education).

### 4. Muhurta & Tara Bala Logic
*   **Goal:** Implement the Navatara system (Janma, Sampat, Vipat, etc.) to determine the auspiciousness of a day relative to a person's birth Nakshatra.
*   **Use Case:** Providing a "Daily Success Score" based on planetary transits over natal nakshatras.

### 5. Complex Chakras (Advanced Visualization)
*   **Sarvatobhadra Chakra:** 9x9 grid mapping Aksharas (Sanskrit phonemes) and Nakshatras for transit Vedhas (obstructions).
*   **Kalachakra:** "Wheel of Time" mapping 28 Nakshatras and directional jumps (Gatis) for life-cycle analysis.

---

## 🛠️ Prerequisite Technical Tasks
1.  **28 Nakshatra System:** Implement **Abhijit** (intercalary) for use in Sarvatobhadra and Kalachakra.
2.  **Sanskrit Phoneme Mapping:** Utility to map names/strings to grid coordinates.
3.  **Transit Hit Engine:** Logical bridge to calculate "Vedhas" (lines of sight) between transiting planets and fixed grid points.

---
*Last Updated: May 20, 2026*
