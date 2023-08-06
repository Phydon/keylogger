use flexi_logger::Logger;
use indicatif::{HumanDuration, ProgressBar, ProgressStyle};
use log::error;
use owo_colors::colored::*;

use std::{
    collections::BTreeMap,
    fs::{self, File},
    io::{self, BufReader, Read, Write},
    path::Path,
    process,
    time::{Duration, Instant},
};

// TODO for testing -> remove
// const KEYLOG_PATH: &str = "keylogtest.txt";
// const WORDCOUNT_PATH: &str = "wordcounttest.txt";
const KEYLOG_PATH: &str = "keylog.txt";
const WORDCOUNT_PATH: &str = "wordcount.txt";

fn main() {
    // handle Ctrl+C
    ctrlc::set_handler(move || {
        println!(
            "{} {} {} {}",
            "Received Ctrl-C!".bold().red(),
            "🤬",
            "Exit program!".bold().red(),
            "☠",
        );
        process::exit(0)
    })
    .expect("Error setting Ctrl-C handler");

    // initialize the logger
    let _logger = Logger::try_with_str("info") // log warn and error
        .unwrap()
        .start()
        .unwrap();

    // Start
    let start = Instant::now();

    // spinner
    let spinner_style = ProgressStyle::with_template("{spinner:.red} {msg}").unwrap();
    let pb = ProgressBar::new_spinner();
    pb.enable_steady_tick(Duration::from_millis(120));
    pb.set_style(spinner_style);

    // read words from keylog file
    pb.set_message(format!("{}", "reading file".truecolor(250, 0, 104)));
    let words = get_words(KEYLOG_PATH).unwrap_or_else(|err| {
        error!("Unable to read file {}: {}", KEYLOG_PATH, err);
        process::exit(1);
    });

    // process words
    pb.set_message(format!("{}", "processing".truecolor(250, 0, 104)));
    let word_map = process_words(words);

    // write to file
    pb.set_message(format!("{}", "populating file".truecolor(250, 0, 104)));
    write_processed_words_to_file(word_map, WORDCOUNT_PATH).unwrap_or_else(|err| {
        error!("Error while writing to file {}: {}", WORDCOUNT_PATH, err);
    });

    // Finish
    pb.finish_with_message(format!("{}", "done in".truecolor(59, 179, 140)));
    println!(
        "{}",
        HumanDuration(start.elapsed())
            .to_string()
            .truecolor(112, 110, 255)
    );
}

fn get_words(path: &str) -> io::Result<Vec<String>> {
    let mut words = Vec::new();

    match Path::new(path).try_exists()? {
        true => {
            let file = File::open(path)?;
            let mut buf_reader = BufReader::new(file);
            let mut content = String::new();
            buf_reader.read_to_string(&mut content)?;

            for line in content.lines() {
                words.push(line.trim().to_string());
            }
        }
        false => {
            error!("Unable to find words to process. File '{path}' doesn`t exist.");
            process::exit(1);
        }
    }

    Ok(words)
}

fn sort_words_by_appearance(word_map: BTreeMap<String, u64>) -> Vec<(String, u64)> {
    let mut sorted_words = Vec::from_iter(word_map);
    sorted_words.sort_by(|&(_, a), &(_, b)| b.cmp(&a));

    sorted_words
}

fn process_words(words: Vec<String>) -> Vec<(String, u64)> {
    let mut word_map = BTreeMap::new();

    for word in words {
        if word_map.contains_key(&word) {
            let word_count = word_map
                .get(&word)
                .expect("Expected a word count for an existing word");
            word_map.insert(word, word_count + 1);
        } else {
            word_map.insert(word, 1);
        }
    }

    let sorted_words = sort_words_by_appearance(word_map);

    sorted_words
}

// TODO bottleneck -> speed up (bufwriter?)
// TODO only write the top 100 appearances??
fn write_processed_words_to_file(word_map: Vec<(String, u64)>, path: &str) -> io::Result<()> {
    let mut file = fs::OpenOptions::new().write(true).create(true).open(path)?;
    let mut counter = 0;

    for (word, count) in word_map {
        if counter >= 100 {
            break;
        }

        let line = format!("{word}: {count}");
        writeln!(file, "{}", line)?;
        counter += 1;
    }

    Ok(())
}
