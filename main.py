import sys
import time

from bot import config, fetchers, slack, state


def main():
    if not config.SLACK_WEBHOOK_URL:
        print('Error: SLACK_WEBHOOK_URL not set', file=sys.stderr)
        sys.exit(1)

    if '--test' in sys.argv:
        slack.send_test()
        return

    current_state = state.load()
    is_first_run = len(current_state) == 0

    if is_first_run:
        print('First run — saving current state, no notifications sent')

    has_new = False

    for board in config.BOARDS:
        name = board['name']
        print(f'Checking {name}...', end=' ', flush=True)

        try:
            notices = fetchers.fetch(board)
        except Exception as e:
            print(f'ERROR: {e}')
            continue

        current_ids = {n['id'] for n in notices}
        seen_ids = set(current_state.get(name, []))

        if not is_first_run:
            new_notices = [n for n in notices if n['id'] not in seen_ids]
            if new_notices:
                print(f'{len(new_notices)} new')
                slack.send_slack(name, board['emoji'], new_notices, board.get('prefix', '세종대 '))
                has_new = True
            else:
                print('no new')
        else:
            print(f'{len(notices)} notices saved')

        current_state[name] = list(seen_ids | current_ids)
        time.sleep(1)

    if not is_first_run and not has_new:
        slack.send_no_updates()

    state.save(current_state)
    print('Done.')


if __name__ == '__main__':
    main()
