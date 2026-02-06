## MODIFIED Requirements

### Requirement: Image Sliding Window Cutter Tool
The system SHALL provide both command-line and graphical user interface tools for cropping images using either a sliding window approach or an automatic alpha-channel DFS algorithm.

#### Scenario: Alpha channel DFS auto-detection
- **WHEN** user selects DFS algorithm mode and provides an image with alpha channel
- **THEN** the system analyzes the alpha channel to find non-transparent continuous regions
- **AND** uses DFS (Depth-First Search) to identify each sprite's boundary
- **AND** calculates bounding boxes for each detected region
- **AND** filters out noise regions (too small areas)

#### Scenario: DFS region detection and cropping
- **WHEN** DFS algorithm detects sprite regions
- **THEN** the system crops each region based on its bounding box
- **AND** saves each cropped sprite as a separate image file
- **AND** maintains original alpha channel in cropped images
- **AND** provides region information (position, size, count)

#### Scenario: GUI algorithm selection
- **WHEN** user opens the GUI tool
- **THEN** the interface provides algorithm selection (Sliding Window / DFS Auto-Detection)
- **AND** in DFS mode, displays detected regions with bounding boxes overlay
- **AND** shows the number of detected regions
- **AND** allows preview before cropping

#### Scenario: DFS algorithm parameters
- **WHEN** using DFS algorithm
- **THEN** the system supports configurable parameters:
  - Minimum region size (to filter noise)
  - Padding/margin around detected regions (optional)
  - Alpha threshold for transparency detection
- **AND** provides reasonable defaults for these parameters

#### Scenario: Fallback to RGB mode
- **WHEN** image has no alpha channel but user selects DFS mode
- **THEN** the system either:
  - Converts image to RGBA and treats white/light pixels as opaque
  - Or suggests using sliding window mode instead
- **AND** provides clear feedback about the mode used
