## ADDED Requirements

### Requirement: Image Sliding Window Cutter Tool
The system SHALL provide a command-line tool that can crop images using a sliding window approach with configurable window size and stride.

#### Scenario: Basic sliding window crop
- **WHEN** user runs the tool with an input image, output directory, window width, and window height
- **THEN** the tool crops the image using a sliding window of the specified size
- **AND** saves each cropped region as a separate image file to the output directory
- **AND** names output files with a pattern that includes the source filename and position (e.g., `source_filename_row_col.png`)

#### Scenario: Custom stride parameter
- **WHEN** user specifies a stride parameter that differs from the window size
- **THEN** the tool uses the specified stride to control the step size between sliding window positions
- **AND** allows overlapping windows when stride is smaller than window size
- **AND** allows gaps between windows when stride is larger than window size

#### Scenario: Batch processing multiple images
- **WHEN** user specifies an input directory containing multiple image files
- **THEN** the tool processes all supported image files in the directory
- **AND** maintains separate output organization for each source image
- **AND** handles errors for individual files without stopping the entire batch

#### Scenario: Boundary handling
- **WHEN** the sliding window extends beyond the image boundaries
- **THEN** the tool handles edge cases appropriately
- **AND** either crops partial windows or skips positions that would extend beyond boundaries
- **AND** provides clear indication of how boundary cases are handled

#### Scenario: Command-line interface
- **WHEN** user runs the tool with required parameters
- **THEN** the tool accepts command-line arguments for:
  - Input directory or file path
  - Output directory path
  - Window width (pixels)
  - Window height (pixels)
  - Stride width (optional, defaults to window width)
  - Stride height (optional, defaults to window height)
- **AND** provides help/usage information when requested
- **AND** validates input parameters and provides clear error messages for invalid inputs

#### Scenario: Progress feedback
- **WHEN** the tool processes images
- **THEN** it displays progress information (e.g., current file being processed, number of crops created)
- **AND** provides summary information upon completion (total files processed, total crops created)
