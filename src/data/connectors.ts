/**
 * Integration registry.
 *
 * Each connector maps an external source into the unified DayRecord schema.
 * In this MVP the demo data stands in for live syncs; the registry defines
 * the integration surface the production sync workers implement.
 */

export interface Connector {
  id: string;
  name: string;
  category: 'Wearables' | 'Finance' | 'Productivity' | 'Lifestyle';
  icon: string;
  status: 'connected' | 'available';
  provides: string[];
  lastSync?: string;
}

export const CONNECTORS: Connector[] = [
  { id: 'oura', name: 'Oura Ring', category: 'Wearables', icon: '💍', status: 'connected', provides: ['Sleep stages', 'HRV', 'Readiness', 'Body temp'], lastSync: '6:42 AM' },
  { id: 'apple-health', name: 'Apple Health', category: 'Wearables', icon: '❤️', status: 'connected', provides: ['Steps', 'Workouts', 'Heart rate', 'Weight'], lastSync: '7:15 AM' },
  { id: 'whoop', name: 'Whoop', category: 'Wearables', icon: '⚡', status: 'available', provides: ['Strain', 'Recovery', 'Sleep coach'] },
  { id: 'garmin', name: 'Garmin', category: 'Wearables', icon: '⌚', status: 'available', provides: ['Training load', 'VO2 max', 'GPS activities'] },
  { id: 'fitbit', name: 'Fitbit', category: 'Wearables', icon: '📟', status: 'available', provides: ['Steps', 'Sleep', 'Active zone minutes'] },
  { id: 'plaid', name: 'Bank & Cards (Plaid)', category: 'Finance', icon: '🏦', status: 'connected', provides: ['Transactions', 'Balances', 'Spending categories'], lastSync: '7:02 AM' },
  { id: 'brokerage', name: 'Investment Accounts', category: 'Finance', icon: '📊', status: 'connected', provides: ['Portfolio value', 'Contributions', 'Allocation'], lastSync: '7:02 AM' },
  { id: 'gcal', name: 'Google Calendar', category: 'Productivity', icon: '📅', status: 'connected', provides: ['Meetings', 'Focus blocks', 'Time analysis'], lastSync: '7:20 AM' },
  { id: 'todoist', name: 'Todoist', category: 'Productivity', icon: '✅', status: 'connected', provides: ['Tasks planned/completed', 'Project progress'], lastSync: '7:20 AM' },
  { id: 'screen-time', name: 'Screen Time', category: 'Lifestyle', icon: '📱', status: 'available', provides: ['App usage', 'Pickups', 'Focus interruptions'] },
  { id: 'myfitnesspal', name: 'MyFitnessPal', category: 'Lifestyle', icon: '🍎', status: 'available', provides: ['Calories', 'Macros', 'Meal logging'] },
];
