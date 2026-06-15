package cmd

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile string
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "runic_router",
	Short: "CAMELOT Command Dispatch",
	Long: `Runic Router — CAMELOT Command Dispatch
Routes all 11 runic commands + 29 Omega runes.`,
	SilenceUsage:  true,
	SilenceErrors: true,
	RunE: func(cmd *cobra.Command, args []string) error {
		isList := viper.GetBool("list")
		detectText := viper.GetString("detect")
		runeName := viper.GetString("rune")
		task := viper.GetString("task")

		if isList {
			fmt.Println("=== Runic Commands ===")
			fmt.Println("  //FLEET")
			fmt.Println("  //BOOT")
			fmt.Println("  //DAWNING")
			fmt.Println("  //FORGE")
			fmt.Println("  //CODEX")
			fmt.Println("  //CONTRACT")
			fmt.Println("  //CLAW")
			fmt.Println("  //SWARM")
			fmt.Println("  //PLAN")
			fmt.Println("  //HEAL")
			fmt.Println("  //GENESIS")
			fmt.Println("  //ASSIMILATE")
			fmt.Println("  //SCAVENGE")
			fmt.Println("  //DEFENSE_INIT")
			fmt.Println("  //vocal")
			fmt.Println("  //SCAN")
			fmt.Println("  //STATUS")
			fmt.Println("  //THINK")
			fmt.Println("  //NANO_SWARM_EXPAND")
			fmt.Println("  //BIFROST_LOCK")
			fmt.Println("  //SCAN_VECTORS")
			fmt.Println("\n=== Omega Runes ===")
			fmt.Println("  Omega_SYNC\n  Omega_PURGE\n  Omega_STATUS\n  Omega_KINETIC\n  Omega_ACTUATE\n  Omega_REFORGE\n  Omega_AUDIT")
			return nil
		}

		if detectText != "" {
			fmt.Printf("Detected rune from text: %s\n", detectText)
			// Mocking detection logic for MVP
			return nil
		}

		if runeName != "" {
			// Connect Go CLI directly to Python control plane logic
			cmdExec := exec.Command("python", "-m", "control_plane.runic_router", "--rune", runeName, "--task", task)
			cmdExec.Stdout = os.Stdout
			cmdExec.Stderr = os.Stderr
			
			err := cmdExec.Run()
			if err != nil {
				return fmt.Errorf("failed to call python control plane: %w", err)
			}
			return nil
		}

		return cmd.Usage()
	},
}

// Execute adds all child commands to the root command and sets flags appropriately.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.runic_router.yaml)")

	rootCmd.Flags().String("rune", "", "The rune to dispatch (e.g. //FORGE or Omega_SYNC)")
	rootCmd.Flags().String("task", "", "The task payload for the rune")
	rootCmd.Flags().String("detect", "", "Text to detect rune from")
	rootCmd.Flags().Bool("list", false, "List all available runic commands")

	viper.BindPFlag("rune", rootCmd.Flags().Lookup("rune"))
	viper.BindPFlag("task", rootCmd.Flags().Lookup("task"))
	viper.BindPFlag("detect", rootCmd.Flags().Lookup("detect"))
	viper.BindPFlag("list", rootCmd.Flags().Lookup("list"))
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		cobra.CheckErr(err)

		viper.AddConfigPath(home)
		viper.SetConfigType("yaml")
		viper.SetConfigName(".runic_router")
	}

	viper.AutomaticEnv()
	viper.ReadInConfig()
}
