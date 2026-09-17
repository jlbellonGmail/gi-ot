// Design tokens (ROADMAP §07, docs/ui-ux/UI-UX-STANDARDS.md §29).
// Referencian las variables CSS de globals.css — se usan dentro de los
// style={{}} inline existentes sin introducir una librería nueva de
// styling (no hay decisión de stack para eso).
export const theme = {
  bg: "var(--color-bg)",
  surface: "var(--color-surface)",
  border: "var(--color-border)",
  text: "var(--color-text)",
  textSecondary: "var(--color-text-secondary)",
  primary: "var(--color-primary)",
  primaryText: "var(--color-primary-text)",
  danger: "var(--color-danger)",
  dangerBg: "var(--color-danger-bg)",
  dangerSolid: "var(--color-danger-solid)",
  warning: "var(--color-warning)",
  warningBg: "var(--color-warning-bg)",
  success: "var(--color-success)",
  successBg: "var(--color-success-bg)",
  successSolid: "var(--color-success-solid)",
  infoBg: "var(--color-info-bg)",
  focus: "var(--color-focus)",
  headerBg: "var(--color-header-bg)",
  headerText: "var(--color-header-text)",
  headerActive: "var(--color-header-active)",
  headerSuccess: "var(--color-header-success)",
} as const;
