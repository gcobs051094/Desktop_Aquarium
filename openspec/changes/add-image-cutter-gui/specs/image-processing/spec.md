## MODIFIED Requirements

### Requirement: Image Sliding Window Cutter Tool
The system SHALL provide both command-line and graphical user interface tools for cropping images using a sliding window approach with configurable window size and stride.

#### Scenario: GUI image preview with grid overlay
- **WHEN** user selects an image file in the folder tree view
- **THEN** the GUI displays the selected image in a preview area
- **AND** overlays a grid showing the sliding window positions based on current parameters
- **AND** updates the grid in real-time when parameters change

#### Scenario: Parameter configuration interface
- **WHEN** user opens the GUI tool
- **THEN** the interface provides input fields for:
  - Window width (pixels)
  - Window height (pixels)
  - Stride X (optional, defaults to window width)
  - Stride Y (optional, defaults to window height)
  - Include partial windows option
- **AND** validates input parameters and provides visual feedback for invalid values
- **AND** updates the preview grid immediately when parameters change

#### Scenario: Folder structure visualization
- **WHEN** user opens the GUI tool
- **THEN** the interface displays a tree view of the resource directory structure
- **AND** shows image files with visual indicators for their status (unprocessed, processed, etc.)
- **AND** allows selection of individual images or folders for batch processing
- **AND** displays folder hierarchy to prevent data confusion

#### Scenario: Classification and loading visualization
- **WHEN** user processes images
- **THEN** the GUI shows which images have been processed
- **AND** displays output folder structure for classification
- **AND** provides visual indicators to distinguish processed vs unprocessed images
- **AND** allows loading existing output folders to visualize classification structure

#### Scenario: Integrated cropping execution
- **WHEN** user configures parameters and clicks the crop button
- **THEN** the GUI executes the cropping operation using the configured parameters
- **AND** displays progress information during processing
- **AND** shows completion status and summary (number of crops created)
- **AND** handles errors gracefully with user-friendly messages
