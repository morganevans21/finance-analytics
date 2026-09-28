# high >= open
# high >= close
# low <= open
# low <= close
                validation_results['ohlc_violations']['raw']['high_lt_low'] = int((ohlc_df['high'] < ohlc_df['low']).sum())
                validation_results['ohlc_violations']['raw']['high_lt_open'] = int((ohlc_df['high'] < ohlc_df['open']).sum())
                validation_results['ohlc_violations']['raw']['high_lt_close'] = int((ohlc_df['high'] < ohlc_df['close']).sum())
                validation_results['ohlc_violations']['raw']['low_gt_open'] = int((ohlc_df['low'] > ohlc_df['open']).sum())
                validation_results['ohlc_violations']['raw']['low_gt_close'] = int((ohlc_df['low'] > ohlc_df['close']).sum())

                total_raw_violations = sum(validation_results['ohlc_violations']['raw'].values())
                if total_raw_violations > 0:
                    print_warning("Raw OHLC relationship violations found:")
                    print(f"  high < low: {validation_results['ohlc_violations']['raw']['high_lt_low']}")
                    print(f"  high < open: {validation_results['ohlc_violations']['raw']['high_lt_open']}")
                    print(f"  high < close: {validation_results['ohlc_violations']['raw']['high_lt_close']}")
                    print(f"  low > open: {validation_results['ohlc_violations']['raw']['low_gt_open']}")
                    print(f"  low > close: {validation_results['ohlc_violations']['raw']['low_gt_close']}")
                else:
                    print_success("No raw OHLC relationship violations found")
            else:
                print_warning("No complete raw OHLC data to validate")
        else:
            print_warning("Missing columns for raw OHLC validation")

        # Check adjusted OHLC relationships
        if all(col in df.columns for col in ['adj_open', 'adj_high', 'adj_low', 'adj_close']):
            # Filter out rows with NULL values in any of these columns
            adj_ohlc_df = df[['adj_open', 'adj_high', 'adj_low', 'adj_close']].dropna()
            if not adj_ohlc_df.empty:
                # high >= low
                validation_results['ohlc_violations']['adjusted']['high_lt_low'] = int((adj_ohlc_df['adj_high'] < adj_ohlc_df['adj_low']).sum())
                validation_results['ohlc_violations']['adjusted']['high_lt_open'] = int((adj_ohlc_df['adj_high'] < adj_ohlc_df['adj_open']).sum())
                validation_results['ohlc_violations']['adjusted']['high_lt_close'] = int((adj_ohlc_df['adj_high'] < adj_ohlc_df['adj_close']).sum())
                validation_results['ohlc_violations']['adjusted']['low_gt_open'] = int((adj_ohlc_df['adj_low'] > adj_ohlc_df['adj_open']).sum())
                validation_results['ohlc_violations']['adjusted']['low_gt_close'] = int((adj_ohlc_df['adj_low'] > adj_ohlc_df['adj_close']).sum())

                total_adj_violations = sum(validation_results['ohlc_violations']['adjusted'].values())
                if total_adj_violations > 0:
                    print_warning("Adjusted OHLC relationship violations found:")
                    print(f"  high < low: {validation_results['ohlc_violations']['adjusted']['high_lt_low']}")
                    print(f"  high < open: {validation_results['ohlc_violations']['adjusted']['high_lt_open']}")
                    print(f"  high < close: {validation_results['ohlc_violations']['adjusted']['high_lt_close']}")
                    print(f"  low > open: {validation_results['ohlc_violations']['adjusted']['low_gt_open']}")
                    print(f"  low > close: {validation_results['ohlc_violations']['adjusted']['low_gt_close']}")
                else:
                    print_success("No adjusted OHLC relationship violations found")
            else:
                print_warning("No complete adjusted OHLC data to validate")
        else:
            print_warning("Missing columns for adjusted OHLC validation")

        print_header("ZERO OR NEGATIVE PRICE CHECK")
        price_cols = ['open', 'high', 'low', 'close', 'adj_open', 'adj_high', 'adj_low', 'adj_close']
        for col in price_cols:
            if col in df.columns:
                # Filter out NULL values
                price_df = df[col].dropna()
                if not price_df.empty:
                    zero_or_neg_count = (price_df <= 0).sum()
                    validation_results['zero_or_negative_prices'][col] = int(zero_or_neg_count)
                    if zero_or_neg_count > 0:
                        print_warning(f"{col}: {zero_or_neg_count} zero or negative values")
                    else:
                        print_status(f"{col}: {zero_or_neg_count} zero or negative values")
                else:
                    print_warning(f"{col}: No non-NULL values to check")
            else:
                print_warning(f"{col}: Column not found")

        print_header("VOLUME CHECK")
        if 'volume' in df.columns:
            # Filter out NULL values
            volume_df = df['volume'].dropna()
            if not volume_df.empty:
                # Check for negative volume
                neg_volume_count = (volume_df < 0).sum()
                validation_results['volume_issues']['negative_count'] = int(neg_volume_count)
                if neg_volume_count > 0:
                    print_warning(f"volume: {neg_volume_count} negative values")
                else:
                    print_status(f"volume: {neg_volume_count} negative values")

                # Check for zero volume (may be legitimate for some securities)
                zero_volume_count = (volume_df == 0).sum()
                validation_results['volume_issues']['zero_count'] = int(zero_volume_count)
                if zero_volume_count > 0:
                    print_status(f"volume: {zero_volume_count} zero values (may be legitimate)")
                else:
                    print_status(f"volume: {zero_volume_count} zero values")
            else:
                print_warning("volume: No non-NULL values to check")
        else:
            print_warning("volume: Column not found")

        print_header("OUTLIER CHECK (Z-SCORE > {})".format(args.threshold))
        # Check for outliers in returns and prices
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        if args.adjusted:
            numeric_cols = ['adj_open', 'adj_high', 'adj_low', 'adj_close', 'volume']

        for col in numeric_cols:
            if col in df.columns:
                # Filter out NULL values
                col_df = df[col].dropna()
                if len(col_df) > 1:  # Need at least 2 values for std dev
                    mean_val = col_df.mean()
                    std_val = col_df.std()
                    if std_val > 0:  # Avoid division by zero
                        z_scores = np.abs((col_df - mean_val) / std_val)
                        outlier_count = (z_scores > args.threshold).sum()
                        validation_results['outliers'][col] = int(outlier_count)
                        if outlier_count > 0:
                            print_warning(f"{col}: {outlier_count} outliers (Z-score > {args.threshold})")
                        else:
                            print_status(f"{col}: {outlier_count} outliers (Z-score > {args.threshold})")
                    else:
                        print_status(f"{col}: Standard deviation is zero (all values identical)")
                else:
                    print_warning(f"{col}: Insufficient data for outlier check (need at least 2 values)")
            else:
                print_warning(f"{col}: Column not found for outlier check")

        print_header("DATA COMPLETENESS CHECK")
        if 'date' in df.columns and 'ticker' in df.columns:
            # Check for missing dates per ticker (expecting roughly daily data)
            try:
                # Group by ticker and check date ranges
                completeness_info = []
                for ticker, group in df.groupby('ticker'):
                    if len(group) > 1:
                        date_range = group['date'].max() - group['date'].min()
                        expected_days = date_range.days + 1
                        actual_days = len(group['date'].unique())
                        completeness_pct = (actual_days / expected_days * 100) if expected_days > 0 else 0
                        completeness_info.append({
                            'ticker': ticker,
                            'date_range_start': group['date'].min(),
                            'date_range_end': group['date'].max(),
                            'expected_days': expected_days,
                            'actual_days': actual_days,
                            'completeness_pct': completeness_pct
                        })

                print(f"{'Ticker':<8} {'Date Range':<25} {'Expected':<10} {'Actual':<10} {'Complete%':<10}")
                print("-" * 75)
                for info in completeness_info:
                    date_range_str = f"{info['date_range_start'].date()} to {info['date_range_end'].date()}"
                    print(f"{info['ticker']:<8} {date_range_str:<25} {info['expected_days']:<10} {info['actual_days']:<10} {info['completeness_pct']:>9.1f}%")

                # Summary
                avg_completeness = np.mean([info['completeness_pct'] for info in completeness_info]) if completeness_info else 0
                print("-" * 75)
                print_success(f"Average date completeness: {avg_completeness:.1f}%")

                # Identify tickers with low completeness
                low_completeness = [info for info in completeness_info if info['completeness_pct'] < 80]
                if low_completeness:
                    print_warning("Tickers with <80% date completeness:")
                    for info in low_completeness:
                        date_range_str = f"{info['date_range_start'].date()} to {info['date_range_end'].date()}"
                        print(f"  {info['ticker']}: {date_range_str} ({info['completeness_pct']:.1f}%)")
                else:
                    print_success("All tickers have >=80% date completeness")

            except Exception as e:
                print_warning(f"Error checking data completeness: {e}")
        else:
            print_warning("Cannot check data completeness - missing date or ticker column")

        print_header("VALIDATION SUMMARY")
        # Calculate overall validation score
        checks_passed = 0
        total_checks = 0

        # NULL value check (critical fields only)
        total_checks += 2  # date, ticker
        if validation_results['null_counts'].get('date', 0) == 0 and validation_results['null_counts'].get('ticker', 0) == 0:
            checks_passed += 2
            print_success("PASS: No NULL values in key identifier columns")
        else:
            print_warning("FAIL: Found NULL values in key identifier columns")

        # Duplicate check
        total_checks += 1
        if validation_results['duplicate_count'] == 0:
            checks_passed += 1
            print_success("PASS: No duplicate records")
        else:
            print_warning("FAIL: Found duplicate records")

        # OHLC check (raw)
        total_checks += 1
        raw_ohlc_pass = sum(validation_results['ohlc_violations']['raw'].values()) == 0
        if raw_ohlc_pass:
            checks_passed += 1
            print_success("PASS: No raw OHLC relationship violations")
        else:
            print_warning("FAIL: Found raw OHLC relationship violations")

        # OHLC check (adjusted)
        total_checks += 1
        adj_ohlc_pass = sum(validation_results['ohlc_violations']['adjusted'].values()) == 0
        if adj_ohlc_pass:
            checks_passed += 1
            print_success("PASS: No adjusted OHLC relationship violations")
        else:
            print_warning("FAIL: Found adjusted OHLC relationship violations")

        # Zero/negative price check (critical fields)
        total_checks += 2  # open, close
        price_check_pass = (validation_results['zero_or_negative_prices'].get('open', 0) == 0 and
                           validation_results['zero_or_negative_prices'].get('close', 0) == 0)
        if price_check_pass:
            checks_passed += 2
            print_success("PASS: No zero or negative open/close prices")
        else:
            print_warning("FAIL: Found zero or negative open/close prices")

        # Overall result
        print("-" * 50)
        if total_checks > 0:
            score = (checks_passed / total_checks) * 100
            print(f"Overall validation score: {score:.1f}% ({checks_passed}/{total_checks} checks passed)")
            if score >= 90:
                print_success("DATA QUALITY: EXCELLENT")
            elif score >= 75:
                print_status("DATA QUALITY: GOOD")
            elif score >= 60:
                print_warning("DATA QUALITY: FAIR")
            else:
                print_error("DATA QUALITY: POOR")
        else:
            print_warning("No validation checks could be performed")

        # Handle duplicate fixing if requested
        if args.fix_duplicates and validation_results['duplicate_count'] > 0:
            print_header("DUPLICATE FIXING")
            print_status("Attempting to remove duplicate records...")
            try:
                with engine.begin() as conn:
                    # Delete duplicates, keeping the first occurrence based on date
                    # This is a simplified approach - in practice, you might want more sophisticated logic
                    result = conn.execute(text("""
                        DELETE FROM prices
                        WHERE ctid NOT IN (
                            SELECT MIN(ctid)
                            FROM prices
                            GROUP BY date, ticker
                        );
                    """))
                    deleted_count = result.rowcount
                    print_success(f"Removed {deleted_count} duplicate records")
                    print_warning("Please re-run validation to confirm duplicates are removed")
            except Exception as e:
                print_error(f"Error fixing duplicates: {e}")

    except Exception as e:
        print_error(f"Error during validation: {e}")
        return 1

    print("=" * 60)
    print_status("Data validation completed")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())