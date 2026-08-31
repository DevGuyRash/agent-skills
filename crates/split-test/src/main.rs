//! Deterministic exchange verification, custody, and derived-view packaging.
#![allow(
    clippy::multiple_crate_versions,
    clippy::print_stderr,
    clippy::print_stdout,
    clippy::redundant_pub_crate,
    clippy::too_many_lines
)]

pub(crate) mod custody;
pub(crate) mod exchange;
pub(crate) mod util;
pub(crate) mod view;

use anyhow::Result;
use clap::{Parser, Subcommand};
use serde_json::Value;
use std::io::Write;
use std::path::PathBuf;
use std::process::ExitCode;

#[derive(Parser, Debug)]
#[command(
    name = "split-test",
    version,
    disable_help_subcommand = true,
    about = "Role-neutral exchange verification, custody, and derived-view packaging"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// Initialize an empty absolute custody root.
    Init { root: PathBuf },
    /// Freeze an open prospective commitment.
    #[command(name = "add-commitment")]
    AddCommitment { root: PathBuf, spec: PathBuf },
    /// Freeze a role-neutral set of work units.
    #[command(name = "add-work-set")]
    AddWorkSet { root: PathBuf, spec: PathBuf },
    /// Freeze one work unit and return its dedicated workspace.
    #[command(name = "prepare-work")]
    PrepareWork {
        root: PathBuf,
        set_id: String,
        unit_id: String,
        spec: PathBuf,
    },
    /// Seal arbitrary work payload and one mechanical terminal record.
    #[command(name = "seal-work")]
    SealWork {
        root: PathBuf,
        set_id: String,
        unit_id: String,
        terminal: PathBuf,
    },
    /// Account for every frozen unit in a work set.
    #[command(name = "close-work-set")]
    CloseWorkSet {
        root: PathBuf,
        set_id: String,
        closure: PathBuf,
    },
    /// Materialize an independently blinded publication.
    Publish { root: PathBuf, spec: PathBuf },
    /// Materialize a separate identity-revealed package after prerequisites close.
    Reveal { root: PathBuf, spec: PathBuf },
    /// Emit the verified controller event projection.
    Events {
        root: PathBuf,
        scope_id: Option<String>,
        #[arg(long, default_value = "jsonl")]
        format: String,
        /// Return only events after this global sequence number.
        #[arg(long)]
        after_sequence: Option<u64>,
        /// Bound the number of emitted events without changing the retained log.
        #[arg(long)]
        max_items: Option<usize>,
    },
    /// Emit a compact externally retainable chain-head receipt.
    Receipt {
        root: PathBuf,
        scope_id: Option<String>,
    },
    /// Verify custody state and every retained sealed payload.
    Status { root: PathBuf },
    /// Verify exact request binding and one-to-one closure accounting.
    Exchange {
        #[command(subcommand)]
        command: ExchangeCommand,
    },
    /// Seal, verify, checkpoint, or serve a derived evidence view.
    View {
        #[command(subcommand)]
        command: ViewCommand,
    },
}

#[derive(Subcommand, Debug)]
#[command(disable_help_subcommand = true)]
enum ExchangeCommand {
    /// Verify a caller-neutral request/result pair without judging its evidence.
    Verify { request: PathBuf, result: PathBuf },
}

#[derive(Subcommand, Debug)]
#[command(disable_help_subcommand = true)]
enum ViewCommand {
    /// Seal an already-authored derived evidence view.
    Seal { root: PathBuf, spec: PathBuf },
    /// Verify a sealed derived evidence view.
    Verify { root: PathBuf },
    /// Emit a compact externally retainable view receipt.
    Receipt { root: PathBuf },
    /// Serve a verified package read-only on a loopback address.
    Serve {
        root: PathBuf,
        #[arg(long, default_value = "127.0.0.1")]
        bind: String,
        #[arg(long, default_value_t = 0)]
        port: u16,
    },
}

fn main() -> ExitCode {
    match execute(Cli::parse()) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error}");
            eprintln!("hint: run split-test --help for the accepted contract");
            ExitCode::from(2)
        }
    }
}

fn execute(cli: Cli) -> Result<()> {
    match cli.command {
        Command::Init { root } => emit(&custody::init(&root)?),
        Command::AddCommitment { root, spec } => emit(&custody::add_commitment(&root, &spec)?),
        Command::AddWorkSet { root, spec } => emit(&custody::add_work_set(&root, &spec)?),
        Command::PrepareWork {
            root,
            set_id,
            unit_id,
            spec,
        } => emit(&custody::prepare_work(&root, &set_id, &unit_id, &spec)?),
        Command::SealWork {
            root,
            set_id,
            unit_id,
            terminal,
        } => emit(&custody::seal_work(&root, &set_id, &unit_id, &terminal)?),
        Command::CloseWorkSet {
            root,
            set_id,
            closure,
        } => emit(&custody::close_work_set(&root, &set_id, &closure)?),
        Command::Publish { root, spec } => emit(&custody::publish(&root, &spec)?),
        Command::Reveal { root, spec } => emit(&custody::reveal(&root, &spec)?),
        Command::Events {
            root,
            scope_id,
            format,
            after_sequence,
            max_items,
        } => emit_jsonl(&custody::events(
            &root,
            scope_id.as_deref(),
            &format,
            after_sequence,
            max_items,
        )?),
        Command::Receipt { root, scope_id } => emit(&custody::receipt(&root, scope_id.as_deref())?),
        Command::Status { root } => emit(&custody::status(&root)?),
        Command::Exchange { command } => match command {
            ExchangeCommand::Verify { request, result } => {
                emit(&exchange::verify(&request, &result)?)
            }
        },
        Command::View { command } => match command {
            ViewCommand::Seal { root, spec } => emit(&view::seal(&root, &spec)?),
            ViewCommand::Verify { root } => emit(&view::verify(&root)?),
            ViewCommand::Receipt { root } => emit(&view::receipt(&root)?),
            ViewCommand::Serve { root, bind, port } => view::serve(&root, &bind, port),
        },
    }
}

fn emit(value: &Value) -> Result<()> {
    let stdout = std::io::stdout();
    let mut locked = stdout.lock();
    serde_json::to_writer(&mut locked, value)?;
    locked.write_all(b"\n")?;
    Ok(())
}

fn emit_jsonl(values: &[Value]) -> Result<()> {
    let stdout = std::io::stdout();
    let mut locked = stdout.lock();
    for value in values {
        serde_json::to_writer(&mut locked, value)?;
        locked.write_all(b"\n")?;
    }
    Ok(())
}
