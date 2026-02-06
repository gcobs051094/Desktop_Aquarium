## MODIFIED Requirements

### Requirement: Image Cutter Tool - Classification Menu Labels
The system SHALL display updated labels in the classification basis dropdown menu.

#### Scenario: Feed label update
- **WHEN** user views the classification basis dropdown menu
- **THEN** the third option displays "飼料 & 錢" instead of "飼料"
- **AND** the internal `classify_basis` value remains `"feed"` (index 2)
- **AND** all existing functionality continues to work as before

### Requirement: Image Cutter Tool - DFS Region Sorting
The system SHALL sort detected regions from left to right based on left boundary x-coordinate.

#### Scenario: DFS detection sorting
- **WHEN** DFS algorithm detects multiple regions
- **THEN** regions are sorted by left boundary x-coordinate (`left`) in ascending order
- **AND** region indices (0, 1, 2, ...) correspond to left-to-right order
- **AND** the previous "top-to-bottom, then left-to-right within rows" logic is removed

#### Scenario: Custom category cropping order
- **WHEN** user crops images with custom categories
- **THEN** regions within each category are sorted by left boundary x-coordinate
- **AND** saved files are named with sequential numbers reflecting left-to-right order (`base_name_000.png`, `base_name_001.png`, ...)
- **AND** the previous "top then left" sorting within categories is removed

#### Scenario: General output cropping order
- **WHEN** user crops images without classification
- **THEN** all regions are sorted by left boundary x-coordinate
- **AND** saved files are named with sequential numbers reflecting left-to-right order (`base_name_sprite_000.png`, `base_name_sprite_001.png`, ...)

#### Scenario: Fish classification mode
- **WHEN** user selects "Fish" classification basis
- **THEN** the system still groups regions into rows (needed for behavior folder mapping)
- **AND** within each row, regions are sorted left-to-right
- **AND** rows are processed top-to-bottom to map to behavior folders
- **AND** this row-based logic only applies to fish classification mode, not affecting other modes

## MODIFIED Requirements

### Requirement: DFS Detection Algorithm
**Previous**: Regions were sorted using a complex algorithm:
- Grouped into rows based on center point y-coordinates
- Sorted within each row by center point x-coordinates
- Used tolerance calculation for row grouping

**Now**: Simplified to direct left-to-right sorting:
- All regions sorted by left boundary x-coordinate (`left`)
- No row grouping or center point calculations
- Simpler and more predictable ordering

### Requirement: Image Cropping Output Order
**Previous**: 
- Custom categories: Sorted by (top, left) - top priority, then left
- General output: Used row-based grouping, then flattened

**Now**:
- Custom categories: Sorted by left only - pure left-to-right
- General output: Direct left-to-right sorting
- Fish classification: Still uses row grouping (for folder mapping), but rows are sorted left-to-right
