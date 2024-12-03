import pytest
from bot.roll import Roll

def test_roll_initialization():
    roll = Roll([1, 4, 2, 3, 5, 6, 3])
    assert roll.dice == [1, 2, 3, 3, 4, 5, 6], 'Dice should be sorted'
    assert roll.num_dice == 7, 'Number of dice should be set'
    assert roll.matches == {1: [1, 2, 4, 5, 6], 2: [3]}, 'Matches should be grouped'
    assert not roll.failed_reroll, 'Should not be a failed reroll'
    assert roll.failed_matches == {}, 'Failed matches should be empty'

def test_matched_dice():
    roll = Roll([1, 1, 2, 3, 3, 3])
    assert roll.matched_dice() == [1, 1, 3, 3, 3]

def test_non_matched_dice():
    roll = Roll([1, 1, 2, 3, 3, 3])
    assert roll.non_matched_dice() == [2]

def test_mark_as_failed_reroll():
    roll = Roll([1, 1, 2, 3, 3, 3])
    roll.mark_as_failed_reroll()
    assert roll.failed_reroll, 'Should be a failed reroll'
    assert roll.failed_matches == {2: [1]}, 'Failed matches should be set'
    assert roll.matches == {1: [2], 3: [3]}, 'Matches should be updated'

def test_mark_as_failed_all_in():
    roll = Roll([1, 1, 2, 3, 3, 3])
    roll.mark_as_failed_all_in()
    assert roll.failed_reroll, 'Should be a failed reroll'
    assert roll.failed_matches == {2: [1], 3: [3]}, 'Failed matches should be set'
    assert roll.matches == {1: [2]}, 'Matches should be updated'

def test_is_better_than():
    roll_with_1_basic_1_critical = Roll([1, 1, 2, 3, 3, 3])
    roll_with_2_basic = Roll([1, 2, 2, 3, 3, 4])
    another_roll_with_2_basic = Roll([1, 1, 2, 5, 6, 6])
    roll_with_3_basic = Roll([4, 4, 5, 5, 6, 6])
    large_roll_with_2_basic_1_critical = Roll([1, 1, 2, 2, 3, 3, 3, 5, 6])
    large_roll_with_4_basic = Roll([1, 1, 2, 3, 3, 5, 5, 6, 6])
    large_roll_with_1_extreme = Roll([1, 2, 2, 2, 2, 3, 4, 5, 6])
    large_roll_with_3_critical = Roll([1, 1, 1, 2, 2, 2, 3, 3, 3])

    assert roll_with_1_basic_1_critical.is_better_than(roll_with_2_basic)
    assert not roll_with_2_basic.is_better_than(roll_with_1_basic_1_critical)
    assert not roll_with_2_basic.is_better_than(another_roll_with_2_basic)
    assert not another_roll_with_2_basic.is_better_than(roll_with_2_basic)
    assert roll_with_3_basic.is_better_than(roll_with_2_basic)
    assert roll_with_1_basic_1_critical.is_better_than(roll_with_3_basic)
    assert large_roll_with_1_extreme.is_better_than(large_roll_with_2_basic_1_critical)
    assert not large_roll_with_2_basic_1_critical.is_better_than(large_roll_with_1_extreme)
    assert large_roll_with_3_critical.is_better_than(roll_with_1_basic_1_critical)
    assert not roll_with_1_basic_1_critical.is_better_than(large_roll_with_3_critical)
    assert large_roll_with_1_extreme.is_better_than(large_roll_with_4_basic)
    assert not large_roll_with_4_basic.is_better_than(large_roll_with_1_extreme)
    assert not large_roll_with_1_extreme.is_better_than(large_roll_with_3_critical)
    assert not large_roll_with_3_critical.is_better_than(large_roll_with_1_extreme)
