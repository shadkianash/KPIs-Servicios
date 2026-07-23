import { createTheme, MantineColorsTuple } from "@mantine/core";

// Cyber blue colors tuple
const cyberBlue: MantineColorsTuple = [
  "#e1f3ff",
  "#badaff",
  "#72b2ff",
  "#268fff",
  "#0072e6",
  "#0059b3",
  "#00458b",
  "#003163",
  "#001d3b",
  "#000a18",
];

export const theme = createTheme({
  primaryColor: "cyberBlue",
  colors: {
    cyberBlue,
  },
  fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  headings: {
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    fontWeight: "700",
  },
  components: {
    Card: {
      defaultProps: {
        padding: "md",
        radius: "md",
        withBorder: true,
      },
    },
    Button: {
      defaultProps: {
        radius: "md",
      },
    },
  },
});
