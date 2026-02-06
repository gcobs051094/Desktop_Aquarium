## MODIFIED Requirements

### Requirement: Image Cutter Tool - DFS Detection Improvements
The system SHALL provide improved DFS (Depth-First Search) region detection with automatic region splitting, better sorting, and logo exclusion capabilities.

#### Scenario: Automatic region splitting
- **WHEN** DFS detects a connected region that may contain multiple independent objects
- **THEN** the system attempts to split the region using multiple strategies:
  - **Horizontal bottleneck detection**: Scans the middle horizontal line of the region, looking for transparent gaps wider than the threshold
  - **Vertical bottleneck detection**: Scans the middle vertical line of the region, looking for transparent gaps taller than the threshold
  - **Connected component analysis**: Re-runs DFS within large regions to find disconnected sub-regions
- **AND** splits the region if a clear bottleneck or multiple components are found
- **AND** only splits if both resulting parts meet the minimum region size requirement

#### Scenario: Split sensitivity parameter
- **WHEN** user adjusts the split sensitivity parameter
- **THEN** the system uses this value (0.05-1.0) as the threshold ratio for bottleneck detection
- **AND** lower values (e.g., 0.1-0.15) make splitting more aggressive (easier to split)
- **AND** higher values (e.g., 0.3-0.5) make splitting more conservative
- **AND** provides a default value of 0.3
- **AND** allows real-time adjustment with automatic re-detection

#### Scenario: Improved sorting algorithm
- **WHEN** DFS detects multiple regions
- **THEN** the system sorts regions using center points instead of top values:
  - Groups regions into rows based on center point y-coordinates
  - Uses a tolerance of 50% of average height or at least 10 pixels
  - Sorts within each row by center point x-coordinates
- **AND** ensures correct top-to-bottom, left-to-right ordering
- **AND** handles regions with varying sizes more accurately

#### Scenario: Manual region deletion
- **WHEN** user right-clicks on a detected region in the preview
- **THEN** the system shows a confirmation dialog
- **AND** upon confirmation, removes the region from the detection list
- **AND** automatically adjusts category indices for all regions after the deleted one
- **AND** updates the preview to reflect the changes
- **AND** displays status information about the deletion

#### Scenario: Automatic logo exclusion
- **WHEN** processing regions in fish classification mode
- **THEN** the system automatically detects and excludes logo regions:
  - Checks for abnormal aspect ratios (width/height > 3.0 or < 0.3)
  - Checks for abnormally large sizes (width or height > 2.5x average)
- **AND** processes all rows (not just the first 7)
- **AND** excludes detected logo regions from cropping
- **AND** allows manual deletion if automatic detection fails

#### Scenario: Fish classification with all rows
- **WHEN** user selects "Fish" classification basis
- **THEN** the system processes all detected rows (not limited to 7)
- **AND** for rows beyond the 7th, uses the last behavior folder (7th folder)
- **AND** automatically excludes logo regions
- **AND** correctly processes fish sprites in row 8 (indices 60-69)
- **AND** creates 7 behavior folders in the source image's parent directory:
  - `1_餓肚子游泳`
  - `2_餓肚子轉向`
  - `3_餓肚子吃`
  - `4_餓肚子死掉`
  - `5_吃飽游泳`
  - `6_吃飽吃`
  - `7_吃飽轉向`
- **AND** saves cropped images into corresponding folders based on row position
- **AND** processes up to 10 regions per row

## ADDED Requirements

### Requirement: Split Sensitivity Control
The system SHALL provide a user-configurable split sensitivity parameter in the DFS parameters panel:
- **Range**: 0.05 to 1.0
- **Default**: 0.3
- **Step**: 0.05
- **Display**: Double spin box with 2 decimal places
- **Help text**: "(越小越容易分割，建議0.1-0.3)"
- **Behavior**: Changes trigger automatic re-detection when auto-update is enabled

### Requirement: Region Deletion Interface
The system SHALL allow users to manually delete detected regions:
- **Trigger**: Right-click on any region bounding box in the preview
- **Confirmation**: Show dialog with region index and coordinates
- **Effect**: Remove region from list, adjust subsequent indices, update preview
- **Feedback**: Display status message with remaining region count

## MODIFIED Requirements

### Requirement: DFS Algorithm Parameters
**Previous**: Supported minimum region size, alpha threshold, and padding.

**Now**: Additionally supports:
- Split sensitivity parameter (0.05-1.0, default 0.3)

### Requirement: Fish Classification with DFS
**Previous**: Processed only the first 7 rows, skipped row 8 (including logo).

**Now**:
- Processes all detected rows
- Automatically excludes logo regions using aspect ratio and size detection
- Row 8 and beyond use the last behavior folder (7th folder)
- Correctly processes fish sprites in all rows (60-69 in row 8)

### Requirement: Region Sorting
**Previous**: Used top values for grouping, which could be inaccurate for regions with varying sizes.

**Now**: Uses center points for more stable and accurate sorting:
- Groups by center point y-coordinates
- Sorts within rows by center point x-coordinates
- Uses improved tolerance calculation (50% of average height or 10 pixels minimum)
