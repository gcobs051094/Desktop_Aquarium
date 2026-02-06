## ADDED Requirements

### Requirement: Image Cutter Category Management
The system SHALL provide a category management interface in the image cutter GUI after DFS detection, allowing users to define custom categories and assign detected regions to categories via interactive bbox selection. Output SHALL be written to the source image's sibling directory, with one folder per category containing cropped images named left-to-right.

#### Scenario: Category management UI after DFS detection
- **WHEN** user has performed DFS region detection on an image
- **THEN** the interface displays a category management section with:
  - A category list showing each category name and its assigned region count
  - A category name input field (used as the output folder name)
  - An "Add category" button
  - A "Delete category" button
- **AND** users may add categories by entering a name and clicking add
- **AND** users may delete the selected category after confirmation

#### Scenario: Interactive region assignment by bbox
- **WHEN** user clicks a category name in the category list
- **THEN** selection mode is enabled on the source image preview
- **AND** the mouse cursor shows a crosshair on the image
- **AND** user may press and drag to draw a bbox (bounding box) on the image
- **AND** on mouse release, all DFS regions whose center or overlap falls within the bbox are assigned to the selected category
- **AND** the category list and preview update to reflect the new assignment (region count and color overlay)

#### Scenario: Visual feedback for category assignment
- **WHEN** categories exist and regions are assigned
- **THEN** the preview displays each category's regions with a distinct color
- **AND** unassigned regions are shown in gray
- **AND** the category list shows each category name with its region count

#### Scenario: Custom category output to source sibling directory
- **WHEN** user has defined one or more categories and assigned regions, and clicks the crop button
- **THEN** the system creates one subfolder per category in the source image's parent directory (sibling to the source image)
- **AND** each subfolder is named with the category name
- **AND** within each category folder, cropped images are saved in left-to-right order as `{base_name}_{order:03d}.png`
- **AND** only regions assigned to that category are cropped into that folder
- **AND** unassigned regions are not cropped when using custom categories

#### Scenario: Switching images clears category state
- **WHEN** user selects a different image in the folder tree
- **THEN** the category list and assignments are cleared for the new image
- **AND** DFS detection runs again for the newly selected image
- **AND** the user may define categories and assign regions again for that image
