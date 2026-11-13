"""Offline tests: python -m unittest discover -s tests"""
import math
import unittest

from sharpbets.calibration import Calibrator, fit, fit_slope
from sharpbets.model import Config, flow_features, kelly_fraction, score_sides, walk_book
from sharpbets.wallets import WalletSkill, score_wallet


def pos(avg, size, pnl, price, t=1):
    return {"avg_price": avg, "total_size": size, "total_pnl": pnl, "current_price": price, "last_event_at": t}


class TestExecution(unittest.TestCase):
    def test_walk_book_sweeps_levels(self):
        asks = [{"price": "0.50", "size": "100"}, {"price": "0.40", "size": "100"}]
        avg, spent, depth = walk_book(asks, 60)  # 40 at 0.40, then 20 at 0.50
        self.assertAlmostEqual(spent, 60)
        self.assertAlmostEqual(avg, 60 / (100 + 40))
        self.assertAlmostEqual(depth, 90)

    def test_kelly(self):
        self.assertAlmostEqual(kelly_fraction(0.6, 0.5), 0.2)
        self.assertEqual(kelly_fraction(0.4, 0.5), 0.0)


class TestSignals(unittest.TestCase):
    def test_sides_are_complementary(self):
        fair0, sides = score_sides(0.6, 0.05, [80, 20], [1000, 9000], Calibrator(None), Config())
        self.assertAlmostEqual(sides[0]["fair"] + sides[1]["fair"], 1.0)
        self.assertAlmostEqual(sides[0]["public"], -sides[1]["public"])

    def test_contrarian_direction(self):
        # Retail piles onto outcome 0, skilled money is on outcome 1 -> fair0 below the price.
        fair0, sides = score_sides(0.6, 0.0, [90, 10], [0, 20000], Calibrator(None), Config())
        self.assertLess(fair0, 0.6)
        self.assertGreater(sides[1]["smart"], 0)
        self.assertLess(sides[1]["public"], 0)

    def test_reverse_line_movement(self):
        # Retail on 0 but price moved toward 1 -> rlm favours 1.
        _, sides = score_sides(0.45, -0.06, [90, 10], [0, 0], Calibrator(None), Config())
        self.assertGreater(sides[1]["rlm"], 0)

    def test_price_signals_off_for_underlying_markets(self):
        _, sides = score_sides(0.45, -0.3, [90, 10], [0, 0], Calibrator(None), Config(), price_signals=False)
        self.assertEqual(sides[1]["rlm"], 0)
        self.assertEqual(sides[1]["fade"], 0)

    def test_correlation_group(self):
        from sharpbets.model import correlation_group
        m = {"events": [{"slug": "btc-nov"}]}
        self.assertEqual(correlation_group(m, {"crypto-prices", "bitcoin"}), "asset:bitcoin")
        self.assertEqual(correlation_group(m, {"nba"}), "event:btc-nov")

    def test_adjustment_is_capped(self):
        cfg = Config()
        fair0, _ = score_sides(0.5, 0.2, [0, 1000], [1e9, 0], Calibrator(None), cfg)
        self.assertLessEqual(math.log(fair0 / (1 - fair0)), cfg.max_adj + 1e-9)

    def test_flow_features(self):
        roster = {"0xsharp": WalletSkill("0xsharp", "s", 0, 0, 50, 50, .6, .1, 3, 3, .1, 2, 1.0)}
        trades = [
            {"token_id": "A", "side": "BUY", "size": 10, "price": 0.5, "proxy_wallet": "0xr1"},
            {"token_id": "B", "side": "SELL", "size": 10, "price": 0.5, "proxy_wallet": "0xr2"},  # = backing A
            {"token_id": "B", "side": "BUY", "size": 1000, "price": 0.5, "proxy_wallet": "0xSHARP"},
        ]
        tickets, smart, names = flow_features(trades, ["A", "B"], roster, 200)
        self.assertEqual(tickets, [2, 0])
        self.assertEqual(smart, [0.0, 500.0])
        self.assertEqual(names, {"s"})


class TestWallets(unittest.TestCase):
    def test_losers_count(self):
        winners = [pos(0.5, 100, 50, 1.0) for _ in range(30)]
        losers = [pos(0.5, 100, -50, 0.0) for _ in range(30)]
        w = score_wallet("w", "w", 1e6, 1e7, winners + losers)
        self.assertAlmostEqual(w.win_rate, 0.5)
        self.assertEqual(w.skill, 0.0)  # coin-flipper: no skill

    def test_consistent_edge_scores(self):
        ps = [pos(0.5, 100, 50, 1.0) for _ in range(70)] + [pos(0.5, 100, -50, 0.0) for _ in range(30)]
        self.assertGreater(score_wallet("w", "w", 1e6, 1e7, ps).skill, 0.5)

    def test_one_hit_wonder_penalised(self):
        ps = [pos(0.3, 1e6, 2e6, 1.0)] + [pos(0.5, 100, -50, 0.0) for _ in range(5)] + \
             [pos(0.5, 100, 50, 1.0) for _ in range(14)]
        w = score_wallet("w", "w", 2e6, 3e6, ps)
        self.assertIn("one-hit", w.note)


class TestCalibration(unittest.TestCase):
    def test_recovers_slope(self):
        import random
        from sharpbets.calibration import expit, logit
        rng = random.Random(0)
        samples = []
        for _ in range(4000):
            p = rng.uniform(0.05, 0.95)
            samples.append((p, int(rng.random() < expit(1.3 * logit(p)))))
        b, se = fit_slope(samples)
        self.assertLess(abs(b - 1.3), 3 * se)
        self.assertGreater(Calibrator(fit(samples))(0.8), 0.8)

    def test_noise_shrinks_to_identity(self):
        samples = [(0.3, 0), (0.7, 1), (0.6, 0), (0.4, 1)] * 3
        self.assertAlmostEqual(Calibrator(fit(samples))(0.3), 0.3, places=2)


if __name__ == "__main__":
    unittest.main()
