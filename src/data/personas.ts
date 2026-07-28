/**
 * Demo personas.
 *
 * Five deliberately different lives, each stressing different parts of the
 * personalization engine: age-banded targets, chronotype-aligned windows,
 * shift-work regularity scoring, situation modes, life-stage finance, and
 * priority-weighted Life Scores. Switching persona re-parameterizes the
 * data generator AND every engine target.
 */

import type { UserProfile } from '../engine/types';

export interface Persona {
  id: string;
  tagline: string;
  profile: UserProfile;
  /** Generator seed so each persona has a stable, distinct history */
  seed: number;
}

export const PERSONAS: Persona[] = [
  {
    id: 'philip',
    tagline: 'Tech worker optimizing everything',
    seed: 20260728,
    profile: {
      name: 'Philip',
      age: 34,
      sex: 'male',
      weightLbs: 192,
      chronotype: 'intermediate',
      lifeStage: 'early-career',
      workPattern: 'standard',
      fitnessLevel: 'intermediate',
      situation: 'normal',
      variableIncome: false,
      savingsBalance: 28400,
      monthlyIncome: 7800,
      monthlyInvestment: 800,
      savingsGoal: 40000,
      savingsGoalLabel: 'House down payment',
      priorities: { health: 4, wealth: 4, productivity: 4, relationships: 3, habits: 3 },
      goals: [
        'Reach 175 lbs by next summer',
        'Save $40k for a house down payment',
        'Ship the side project',
        'Call parents at least weekly',
      ],
    },
  },
  {
    id: 'maya',
    tagline: 'ICU nurse on rotating nights',
    seed: 31415926,
    profile: {
      name: 'Maya',
      age: 29,
      sex: 'female',
      weightLbs: 141,
      chronotype: 'evening',
      lifeStage: 'early-career',
      workPattern: 'shift',
      fitnessLevel: 'intermediate',
      situation: 'normal',
      variableIncome: false,
      savingsBalance: 9200,
      monthlyIncome: 6100,
      monthlyInvestment: 400,
      savingsGoal: 20000,
      savingsGoalLabel: 'Emergency fund + travel',
      priorities: { health: 5, wealth: 3, productivity: 2, relationships: 4, habits: 3 },
      goals: [
        'Survive night rotations without wrecking my health',
        'Build a 6-month emergency fund',
        'Run a 10k in the spring',
      ],
    },
  },
  {
    id: 'david',
    tagline: 'New dad running on fumes',
    seed: 27182818,
    profile: {
      name: 'David',
      age: 38,
      sex: 'male',
      weightLbs: 205,
      chronotype: 'intermediate',
      lifeStage: 'parent-young-kids',
      workPattern: 'flexible',
      fitnessLevel: 'beginner',
      situation: 'new-baby',
      variableIncome: false,
      savingsBalance: 41000,
      monthlyIncome: 9200,
      monthlyInvestment: 600,
      savingsGoal: 60000,
      savingsGoalLabel: 'College fund start + bigger car',
      priorities: { health: 3, wealth: 4, productivity: 3, relationships: 5, habits: 2 },
      goals: [
        'Stay sane through the first year',
        'Protect date night with my partner',
        'Get back to 3 workouts a week — eventually',
      ],
    },
  },
  {
    id: 'rosa',
    tagline: 'Retired teacher, thriving at 67',
    seed: 16180339,
    profile: {
      name: 'Rosa',
      age: 67,
      sex: 'female',
      weightLbs: 152,
      chronotype: 'morning',
      lifeStage: 'retired',
      workPattern: 'not-working',
      fitnessLevel: 'beginner',
      situation: 'normal',
      variableIncome: false,
      savingsBalance: 610000,
      monthlyIncome: 4300, // pension + withdrawals
      monthlyInvestment: 0,
      savingsGoal: 650000, // preservation target
      savingsGoalLabel: 'Nest egg preservation',
      priorities: { health: 5, wealth: 3, productivity: 2, relationships: 5, habits: 4 },
      goals: [
        'Stay strong enough to travel and lift grandkids',
        'Keep withdrawals under 4%',
        'See friends or family most days',
      ],
    },
  },
  {
    id: 'sam',
    tagline: 'Junior year, night owl, ramen budget',
    seed: 14142135,
    profile: {
      name: 'Sam',
      age: 21,
      sex: 'other',
      weightLbs: 158,
      chronotype: 'evening',
      lifeStage: 'student',
      workPattern: 'flexible',
      fitnessLevel: 'beginner',
      situation: 'crunch', // finals week
      variableIncome: true, // part-time gig income
      savingsBalance: 900,
      monthlyIncome: 1400,
      monthlyInvestment: 50,
      savingsGoal: 2000,
      savingsGoalLabel: 'Starter emergency fund',
      priorities: { health: 3, wealth: 2, productivity: 5, relationships: 3, habits: 2 },
      goals: [
        'Pass finals without an all-nighter spiral',
        'Build a $2k starter emergency fund',
        'Cook more than I DoorDash',
      ],
    },
  },
];

export function getPersona(id: string): Persona {
  return PERSONAS.find((p) => p.id === id) ?? PERSONAS[0];
}
