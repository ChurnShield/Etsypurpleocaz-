# =============================================================================
# workflows/auto_listing_creator/tools/svg_botanical/
#
# Fine-line botanical tattoo SVG/PNG bundle generation pipeline.
#
# Modules:
#   botanical_primitives    - ~30 reusable SVG path shapes
#   botanical_compositions  - Composition rules per category
#   botanical_categories    - Design registry with metadata
#   svg_generator_tool      - BaseTool: generates all SVG files
#   format_converter_tool   - BaseTool: SVG -> PNG, DXF, PDF, EPS
#   bundle_packager_tool    - BaseTool: creates ZIP for Etsy
#   thumbnail_generator_tool - BaseTool: 5-page Etsy listing images
# =============================================================================
