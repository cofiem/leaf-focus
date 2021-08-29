from leaf_focus.command.entry import Entry

if __name__ == "__main__":
    entry = Entry()
    parser = entry.build()
    entry.run(parser)
