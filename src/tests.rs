#[cfg(test)]
mod cli_tests {
    use std::process::Command;

    fn get_binary_path() -> String {
        // Use debug binary for tests
        let manifest_dir = env!("CARGO_MANIFEST_DIR");
        format!("{}/target/debug/listen", manifest_dir)
    }

    #[test]
    fn test_help_flag() {
        let output = Command::new(get_binary_path())
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.to_lowercase().contains("usage"));
        assert!(stdout.contains("--file"));
        assert!(stdout.contains("--language"));
        assert!(stdout.contains("--model"));
    }

    #[test]
    fn test_version_flag() {
        let output = Command::new(get_binary_path())
            .arg("--version")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("listen"));
        assert!(stdout.contains("2.1.0"));
    }

    #[test]
    fn test_help_shows_file_mode() {
        let output = Command::new(get_binary_path())
            .arg("-h")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--file") || stdout.contains("-f"));
        assert!(stdout.contains("Transcribe audio from file"));
    }

    #[test]
    fn test_file_not_found() {
        let output = Command::new(get_binary_path())
            .arg("-f")
            .arg("/nonexistent/file.mp3")
            .output()
            .expect("Failed to execute command");

        assert!(!output.status.success());
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(
            stderr.to_lowercase().contains("file not found") ||
            stderr.to_lowercase().contains("not found")
        );
    }

    #[test]
    fn test_language_argument() {
        let output = Command::new(get_binary_path())
            .arg("--language")
            .arg("en")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        // Should show help (help takes precedence)
        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--language"));
    }

    #[test]
    fn test_model_argument() {
        let output = Command::new(get_binary_path())
            .arg("--model")
            .arg("tiny")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--model"));
    }

    #[test]
    fn test_verbose_flag() {
        let output = Command::new(get_binary_path())
            .arg("-v")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--verbose") || stdout.contains("-v"));
    }

    #[test]
    fn test_json_flag() {
        let output = Command::new(get_binary_path())
            .arg("-j")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--json") || stdout.contains("-j"));
    }

    #[test]
    fn test_quiet_flag() {
        let output = Command::new(get_binary_path())
            .arg("-q")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--quiet") || stdout.contains("-q"));
    }

    #[test]
    fn test_vad_flag() {
        let output = Command::new(get_binary_path())
            .arg("--vad")
            .arg("2.0")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--vad"));
    }

    #[test]
    fn test_signal_mode_flag() {
        let output = Command::new(get_binary_path())
            .arg("--signal-mode")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--signal-mode"));
    }

    #[test]
    fn test_fast_mode_flag() {
        let output = Command::new(get_binary_path())
            .arg("--fast-mode")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--fast-mode"));
    }

    #[test]
    fn test_codevoice_flag() {
        let output = Command::new(get_binary_path())
            .arg("--codevoice")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--codevoice"));
    }

    #[test]
    fn test_output_file_flag() {
        let output = Command::new(get_binary_path())
            .arg("-o")
            .arg("output.txt")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--output") || stdout.contains("-o"));
    }

    #[test]
    fn test_status_file_flag() {
        let output = Command::new(get_binary_path())
            .arg("--status-file")
            .arg("status.json")
            .arg("--help")
            .output()
            .expect("Failed to execute command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("--status-file"));
    }
}

#[cfg(test)]
mod config_tests {
    use crate::cli::Args;
    use crate::config::Config;
    use clap::Parser;

    #[test]
    fn test_config_defaults() {
        let args = Args::parse_from(&["listen"]);
        let config = Config::from_args(&args).unwrap();

        assert_eq!(config.language, "es");
        assert_eq!(config.model, "base");
        assert!(!config.vad_enabled);
        assert!(!config.signal_mode);
        assert!(!config.quiet);
        assert!(!config.verbose);
    }

    #[test]
    fn test_config_with_vad() {
        let args = Args::parse_from(&["listen", "--vad", "3.0"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.vad_enabled);
        assert_eq!(config.vad_duration, 3.0);
    }

    #[test]
    fn test_config_with_language() {
        let args = Args::parse_from(&["listen", "--language", "en"]);
        let config = Config::from_args(&args).unwrap();

        assert_eq!(config.language, "en");
    }

    #[test]
    fn test_config_with_model() {
        let args = Args::parse_from(&["listen", "--model", "tiny"]);
        let config = Config::from_args(&args).unwrap();

        assert_eq!(config.model, "tiny");
    }

    #[test]
    fn test_config_verbose() {
        let args = Args::parse_from(&["listen", "--verbose"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.verbose);
    }

    #[test]
    fn test_config_quiet() {
        let args = Args::parse_from(&["listen", "--quiet"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.quiet);
    }

    #[test]
    fn test_config_json() {
        let args = Args::parse_from(&["listen", "--json"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.json);
    }

    #[test]
    fn test_config_signal_mode() {
        let args = Args::parse_from(&["listen", "--signal-mode"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.signal_mode);
    }

    #[test]
    fn test_config_fast_mode() {
        let args = Args::parse_from(&["listen", "--fast-mode"]);
        let config = Config::from_args(&args).unwrap();

        assert!(config.fast_mode);
    }
}
