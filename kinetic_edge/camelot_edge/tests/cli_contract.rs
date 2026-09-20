use std::process::Command;

fn run_edge(args: &[&str]) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_camelot-edge"))
        .args(args)
        .output()
        .expect("edge binary runs")
}

#[test]
fn status_command_does_not_open_a_listener() {
    let output = run_edge(&["status"]);
    assert!(output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("listener=disabled"));
}

#[test]
fn unknown_command_fails_closed() {
    assert!(!run_edge(&["execute-shell"]).status.success());
}
