## MODIFIED Requirements

### Requirement: Image Cutter Tool
The system SHALL provide a graphical user interface tool for cropping images using an automatic alpha-channel DFS algorithm. The tool SHALL support automatic classification of fish sprites into behavior folders based on row and column positions.

#### Scenario: DFS-only algorithm mode
- **WHEN** user opens the GUI tool
- **THEN** the interface provides only DFS (Depth-First Search) algorithm mode
- **AND** automatically detects non-transparent regions in the selected image
- **AND** displays detected regions with bounding boxes and sequence numbers
- **AND** allows preview before cropping

#### Scenario: DFS region detection and preview
- **WHEN** user selects an image file in the folder tree view
- **THEN** the system automatically detects sprite regions using DFS algorithm
- **AND** displays the image with bounding boxes overlay showing detected regions
- **AND** numbers each region sequentially (top-to-bottom, left-to-right)
- **AND** updates the preview when DFS parameters change

#### Scenario: DFS algorithm parameters
- **WHEN** using DFS algorithm
- **THEN** the system supports configurable parameters:
  - Minimum region size (to filter noise)
  - Padding/margin around detected regions (optional)
  - Alpha threshold for transparency detection
- **AND** provides reasonable defaults for these parameters
- **AND** allows real-time parameter adjustment with automatic re-detection

#### Scenario: Fish classification with DFS
- **WHEN** user selects "Fish" classification basis and processes an image with DFS
- **THEN** the system automatically groups detected regions into rows (using row tolerance)
- **AND** processes only the first 7 rows, with up to 10 regions per row
- **AND** creates 7 behavior folders in the source image's parent directory:
  - `1_餓肚子游泳`
  - `2_餓肚子轉向`
  - `3_餓肚子吃`
  - `4_餓肚子死掉`
  - `5_吃飽游泳`
  - `6_吃飽吃`
  - `7_吃飽轉向`
- **AND** saves cropped images into corresponding folders based on row position
- **AND** skips regions beyond row 7 or column 10 (including logo)
- **AND** names files as `{base_name}_{order:03d}.png` where order = row * 10 + col

#### Scenario: General output without classification
- **WHEN** user selects "No classification" and processes an image with DFS
- **THEN** the system crops all detected regions
- **AND** saves cropped images to the specified output directory
- **AND** names files as `{base_name}_sprite_{idx:03d}.png` in sequential order

#### Scenario: Folder structure visualization
- **WHEN** user opens the GUI tool
- **THEN** the interface displays a tree view of the resource directory structure
- **AND** shows image files with visual indicators for their status (unprocessed, processed)
- **AND** checks for processed files in:
  - Fish behavior folders (for fish classification)
  - Output directory (for general DFS output)
- **AND** highlights processed images in green

#### Scenario: Integrated cropping execution
- **WHEN** user configures DFS parameters and clicks the crop button
- **THEN** the GUI executes the cropping operation using DFS algorithm
- **AND** displays progress information during processing
- **AND** shows completion status and summary (number of crops created)
- **AND** handles errors gracefully with user-friendly messages
- **AND** automatically refreshes folder structure to show processed status

## REMOVED Requirements

### Requirement: Sliding Window Algorithm
**Reason**: User confirmed that sliding window cropping is no longer needed. The tool now focuses exclusively on DFS automatic region detection, which provides better accuracy for sprite sheets with irregular layouts.

**Migration**: Users who previously used sliding window mode should use DFS mode instead. The DFS algorithm automatically detects sprite boundaries without requiring manual window size and stride configuration.

### Requirement: Algorithm Selection Interface
**Reason**: With only one algorithm (DFS) supported, the algorithm selection dropdown is no longer necessary.

**Migration**: The GUI now defaults to DFS mode. All cropping operations use DFS automatic detection.

### Requirement: Sliding Window Parameters
**Reason**: Window width, height, and stride parameters are specific to sliding window algorithm and are no longer needed.

**Migration**: Users should configure DFS parameters (minimum region size, alpha threshold, padding) instead.
