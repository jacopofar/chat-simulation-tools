import json
from random import shuffle

# over how many candidates one must choose
SET_SIZE = 20


def main():
    atoms = open('conversation_atoms.shuffled.jsonl')
    results = open('atoms_results.jsonl', 'w')
    done_count = 0
    correct_count = 0
    while True:
        done_count += 1
        original_context = json.loads(next(atoms))
        candidates = [original_context['reply']]
        for _ in range(SET_SIZE):
            candidates.append(json.loads(next(atoms))['reply'])
        shuffle(candidates)
        print(f'\n\n SAMPLE #{done_count}:\n\n')
        for line in original_context['context']:
            print(f'    {line[0]}: {line[1]}')
        print('\nChoices:\n')
        for i, c in enumerate(candidates):
            print(f'{i}:  {c}')
        try:
            chosen = int(input('Proper answer? '))
        except KeyboardInterrupt:
            print('\n Interrupted...\n')
            print('done:', done_count)
            print('correct:', correct_count)
            print('Bye!')
            results.close()
            quit()
        # note that the same text could appear twice, it's fine
        # the validation is on the text content and not the index
        is_correct = (candidates[chosen] == original_context['reply'])
        if is_correct:
            correct_count += 1
        results.write(json.dumps(dict(
            candidates=candidates,
            choice_id=chosen,
            correct=is_correct,
            context=original_context
        )))
        results.write('\n')


if __name__ == '__main__':
    main()
