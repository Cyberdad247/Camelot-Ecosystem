import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.camelotos.mobilebridge",
  appName: "Camelot Device Bridge",
  webDir: "dist",
  server: { androidScheme: "https" },
  plugins: {
    LocalNotifications: { smallIcon: "ic_stat_icon_config_sample", iconColor: "#63dcc5" },
  },
};

export default config;
