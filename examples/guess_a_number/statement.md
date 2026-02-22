# Guess a Number

This problem is *interactive* - the judge will change its output based on your own.

I'm thinking of a number between $1$ and $100000$ - Take some guesses!

Every time you guess a number, I'll let you know if my number is higher, lower, or on the money!

## Interaction

Your program should initiate interaction, by outputing a number $x$ between $1$ and $100000$.

The judge will then respond one of four ways.

* `YES` if you correctly guessed the number. Your program you then exit when reading this.
* `HIGHER` if the number to guess is higher than the number you provided.
* `LOWER` if the number to guess is lower than the number you provided.
* `DONE` if you did not guess the number and you've run out of queries.

## Constraints

* The number to guess will be some $x$ satisfying $1 \leq x \leq 100000$.

## Test Set A (50 points)

For test set A, you will have 51 queries to guess the number

## Test Set B (50 points)

For test set B, you will have 15 queries to guess the number

## Example Interaction

Suppose the number to guess was 169. Interaction could have gone as follows:
| Process | Judge |
|----|----|
| `1000` |  |
|  | `LOWER` |
| `50` |  |
|  | `HIGHER` |
| `100` |  |
|  | `HIGHER` |
| `150` |  |
|  | `HIGHER` |
| `170` | |
|  | `LOWER` |
| `169` | |
|  | `YES` |