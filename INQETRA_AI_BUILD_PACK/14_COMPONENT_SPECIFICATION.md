# Component Specification

## App shell
`InqetraSidebar`, `TopUtilityBar`, `ProjectRail`, `ContextInspector`, `MobileNav`.

## Core primitives
Button; IconButton; Input; Textarea; Select; MultiSelect; Checkbox; Radio; Tabs; Chip; StatusBadge; Card; Panel; KPI; Drawer; Modal; Toast; Tooltip; DataTable; EmptyState; Skeleton; ErrorPanel.

## Research components
ResearchQuestionCard; AimCard; ObjectiveList; MethodCard; DatasetRequirementCard; RelationshipMatrix; ReadinessPanel; DataGapRadar; AnalysisPipeline; EvidenceTrace; NoteEditor; AbstractComposer.

## Dataset components
DatasetCard; DatasetRow; DatasetHeader; AuthorityBadge; AccessBadge; LicenceBadge; ProvenanceStrip; VariableBrowser; CoverageSummary; TemporalBar; DatasetCompareGrid; BasketDrawer; CandidateCard; SourceHealthCard.

## Interaction mechanics
Hover translate(-1px,-1px), deepen shadow. Active translate(+2/+3px,+2/+3px), collapse shadow. Focus-visible violet 3px outline with offset. Disabled state retains readable border/text and removes hard shadow.

## Matrix
Sticky top/left headers. Cells are buttons, not decorative blocks. Keyboard arrows move; Enter opens cell editor. State includes icon/text plus colour.
