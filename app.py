import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from data import Data
import time
import urllib

class App:
    def __init__(self):
        self.data_instance = Data()
        self.appSetup()

    def appSetup(self):
        #st.set_page_config(layout="wide")
        st.title("Galaxy Research Dashboard")

        # Create a horizontal navigation bar
        selected_tab = st.radio(
            "Select a Tab",
            ("Home", "Ethereum Validators", "Ethereum L2"),
            key="navigation",
            label_visibility="collapsed",
            horizontal=True,
        )

        # Add icons or emojis to the navigation options
        tab_icons = {
            "Home": "🏠",
            "Ethereum Validators": "🔒",
            "Ethereum L2": "⚡",
        }

        # Customize the navigation bar style
        st.markdown(
            """
            <style>
            .streamlit-expanderHeader {
                font-size: 18px;
                font-weight: bold;
            }
            .streamlit-expanderHeader:hover {
                color: #ff4b4b;
            }
            .streamlit-expander {
                border-radius: 10px;
                border: 2px solid #ff4b4b;
                padding: 10px;
                margin-bottom: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Display the selected tab content
        if selected_tab == "Home":
            self.tabHome()
        elif selected_tab == "Ethereum Validators":
            self.tabEthereumValidators()
        elif selected_tab == "Ethereum L2":
            self.tabEthereumL2()

    def tabHome(self):
        st.header("Featured Charts")

# Validators Tab ---------------------------------------------------------------------------------
    def tabEthereumValidators(self):
        st.header("Validator Queue Data")

        # Fetch data
        with st.spinner('Fetching data...'):
            df_entry_wait = self.data_instance.fetchEntryWait()
            df_exit_wait = self.data_instance.fetchExitWait()
            df_validators_churn = self.data_instance.fetchValidatorsAndChurn()
            df_apr = self.data_instance.fetchAPR()
            df_staked_amount = self.data_instance.fetchStakedAmount()
            df_entry_queue = self.data_instance.fetchEntryQueue()
            df_exit_queue = self.data_instance.fetchExitQueue()
            df_staking_apy = self.data_instance.fetchStakingAPY()

        if (
            df_entry_wait is not None
            and not df_entry_wait.empty
            and df_exit_wait is not None
            and not df_exit_wait.empty
            and df_validators_churn is not None
            and not df_validators_churn.empty
            and df_apr is not None
            and not df_apr.empty
            and df_staked_amount is not None
            and not df_staked_amount.empty
            and df_entry_queue is not None
            and not df_entry_queue.empty
            and df_exit_queue is not None
            and not df_exit_queue.empty
        ):
            # Create a placeholder for the success message
            success_message = st.empty()
            success_message.success("Data successfully fetched.")

            # Wait for 1 seconds and then clear the success message
            time.sleep(1)
            success_message.empty()

            # Display APR and staked ETH amount in big bold numbers
            col1, col2 = st.columns(2)
            with col1:
                latest_apr = df_apr['apr'].iloc[-1]
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 48px; font-weight: bold;'>{latest_apr:.2f}%</div><div style='font-size: 24px;'>Staking APR</div></div>", unsafe_allow_html=True)
            with col2:
                latest_staked_amount = df_staked_amount['staked_amount'].iloc[-1] / 1_000_000
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 48px; font-weight: bold;'>{latest_staked_amount:,.2f}M</div><div style='font-size: 24px;'>Staked ETH</div></div>", unsafe_allow_html=True)

            # Period selection bar
            time_periods = {'7d': 7, '30d': 30, '90d': 90, '180d': 180, '365d': 365, 'All': None}
            selected_period = st.selectbox("Select Time Period", list(time_periods.keys()), index=2, label_visibility='collapsed')

            # Filter data based on selected time period
            if time_periods[selected_period] is not None:
                max_date = df_entry_wait['Date'].max()
                min_date = max_date - pd.Timedelta(days=time_periods[selected_period] - 1)
                mask_entry_wait = (df_entry_wait['Date'] >= min_date) & (df_entry_wait['Date'] <= max_date)
                mask_exit_wait = (df_exit_wait['Date'] >= min_date) & (df_exit_wait['Date'] <= max_date)
                mask_validators_churn = (df_validators_churn['Date'] >= min_date) & (df_validators_churn['Date'] <= max_date)
                mask_apr = (df_apr['Date'] >= min_date) & (df_apr['Date'] <= max_date)
                mask2 = (df_staked_amount['Date'] >= min_date) & (df_staked_amount['Date'] <= max_date)
                mask3 = (df_entry_queue['Date'] >= min_date) & (df_entry_queue['Date'] <= max_date)
                mask4 = (df_exit_queue['Date'] >= min_date) & (df_exit_queue['Date'] <= max_date)
                mask_staking_apy = (df_staking_apy['Date'] >= min_date) & (df_staking_apy['Date'] <= max_date)
                df_entry_wait = df_entry_wait.loc[mask_entry_wait]
                df_exit_wait = df_exit_wait.loc[mask_exit_wait]
                df_validators_churn = df_validators_churn.loc[mask_validators_churn]
                df_apr = df_apr.loc[mask_apr]
                df_staked_amount = df_staked_amount.loc[mask2]
                df_entry_queue = df_entry_queue.loc[mask3]
                df_exit_queue = df_exit_queue.loc[mask4]
                df_staking_apy = df_staking_apy.loc[mask_staking_apy]

            # Side by side entry/exit wait charts
            col1, col2 = st.columns(2)
            with col1:
                fig_entry_wait = go.Figure()
                fig_entry_wait.add_trace(go.Scatter(x=df_entry_wait['Date'], y=df_entry_wait['entry_wait'], mode='lines', name='Entry Wait'))
                fig_entry_wait.update_layout(
                    title='Entry Wait (Days)<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                    xaxis_title='Date',
                    yaxis_title='Entry Wait (Days)',
                    legend=dict(x=0, y=1, orientation='h')
                )
                st.plotly_chart(fig_entry_wait, use_container_width=True)

                csv_entry_wait = df_entry_wait.to_csv(index=False)
                st.download_button(label="CSV", data=csv_entry_wait, file_name='entry_wait.csv', mime='text/csv')

            with col2:
                fig_exit_wait = go.Figure()
                fig_exit_wait.add_trace(go.Scatter(x=df_exit_wait['Date'], y=df_exit_wait['exit_wait'], mode='lines', name='Exit Wait'))
                fig_exit_wait.update_layout(
                    title='Exit Wait (Days)<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                    xaxis_title='Date',
                    yaxis_title='Exit Wait (Days)',
                    legend=dict(x=0, y=1, orientation='h')
                )
                st.plotly_chart(fig_exit_wait, use_container_width=True)

                csv_exit_wait = df_exit_wait.to_csv(index=False)
                st.download_button(label="CSV", data=csv_exit_wait, file_name='exit_wait.csv', mime='text/csv')

            # Staking APY stacked bar chart
            fig_staking_apy = go.Figure()
            fig_staking_apy.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['Yearly Issuance APY'] * 100, name='Inflation'))
            fig_staking_apy.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['Yearly MEV APY'] * 100, name='MEV'))
            fig_staking_apy.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['Yearly TIPS APY'] * 100, name='Tips'))
            fig_staking_apy.update_layout(
                title='Staking APY Breakdown<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Coin Metrics, Flipside Crypto</span>',
                xaxis_title='Date',
                yaxis_title='APY (%)',
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_staking_apy, use_container_width=True)

            csv_staking_apy = df_staking_apy[['Date', 'Yearly Issuance APY', 'Yearly MEV APY', 'Yearly TIPS APY']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_staking_apy, file_name='staking_apy_breakdown.csv', mime='text/csv')

            # Validator Revenue by Source stacked bar chart
            fig_validator_revenue = go.Figure()
            fig_validator_revenue.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['Total Native Issuance'], name='Inflation'))
            fig_validator_revenue.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['MEV'], name='MEV'))
            fig_validator_revenue.add_trace(go.Bar(x=df_staking_apy['Date'], y=df_staking_apy['TIPS'], name='Tips'))
            fig_validator_revenue.update_layout(
                title='Validator Revenue by Source (ETH)<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Coin Metrics, Flipside Crypto</span>',
                xaxis_title='Date',
                yaxis_title='Revenue (ETH)',
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_validator_revenue, use_container_width=True)

            csv_validator_revenue = df_staking_apy[['Date', 'Total Native Issuance', 'MEV', 'TIPS']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_validator_revenue, file_name='validator_revenue.csv', mime='text/csv')

            # Validator count and churn chart
            fig_validators_churn = go.Figure()

            fig_validators_churn.add_trace(
                go.Scatter(
                    x=df_validators_churn['Date'],
                    y=df_validators_churn['validators'],
                    mode='lines',
                    name='Validators',
                )
            )

            fig_validators_churn.add_trace(
                go.Scatter(
                    x=df_validators_churn['Date'],
                    y=df_validators_churn['churn'],
                    mode='lines',
                    name='Exit Churn',
                    yaxis='y2',
                )
            )

            # Create a copy of the DataFrame for the second churn line
            df_validators_churn_hardcoded = df_validators_churn.copy()

            # Find the index of March 13, 2024
            hardcoded_date = '2024-03-13'
            hardcoded_date_timestamp = pd.to_datetime(hardcoded_date)

            # Check if the hardcoded date is within the date range of the DataFrame
            if hardcoded_date_timestamp >= df_validators_churn_hardcoded['Date'].min():
                # Set the churn value to 8 from March 13, 2024 onwards
                df_validators_churn_hardcoded.loc[df_validators_churn_hardcoded['Date'] >= hardcoded_date_timestamp, 'churn'] = 8
            else:
                # Set the entire churn column to 8 if the hardcoded date is outside the date range
                df_validators_churn_hardcoded['churn'] = 8

            fig_validators_churn.add_trace(
                go.Scatter(
                    x=df_validators_churn_hardcoded['Date'],
                    y=df_validators_churn_hardcoded['churn'],
                    mode='lines',
                    name='Entry Churn',
                    yaxis='y2',
                )
            )

            fig_validators_churn.update_layout(
                title='Validators and Churn<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                xaxis_title='Date',
                yaxis_title='Validators',
                yaxis2=dict(title='Churn', side='right', overlaying='y'),
                legend=dict(x=0, y=1, orientation='h')
            )

            st.plotly_chart(fig_validators_churn, use_container_width=True)

            # Merge the original and hardcoded DataFrames
            df_validators_churn_merged = pd.merge(df_validators_churn, df_validators_churn_hardcoded[['Date', 'churn']], on='Date', suffixes=('_exit', '_entry'))

            # Rename the churn columns
            df_validators_churn_merged.rename(columns={'churn_exit': 'Exit Churn', 'churn_entry': 'Entry Churn'}, inplace=True)

            csv_validators_churn = df_validators_churn_merged.to_csv(index=False)
            st.download_button(label="CSV", data=csv_validators_churn, file_name='validators_churn.csv', mime='text/csv')

            # Staked ETH amount and % of total ETH staked
            fig_staked_amount = go.Figure()
            fig_staked_amount.add_trace(go.Scatter(x=df_staked_amount['Date'], y=df_staked_amount['staked_amount'], mode='lines', name='Staked Amount'))
            fig_staked_amount.add_trace(go.Scatter(x=df_staked_amount['Date'], y=df_staked_amount['staked_percent'], mode='lines', name='Staked Percent', yaxis='y2'))
            fig_staked_amount.update_layout(
                title='Staked Amount and Percentage<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                xaxis_title='Date',
                yaxis_title='Staked Amount',
                yaxis2=dict(title='Staked Percent', side='right', overlaying='y'),
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_staked_amount, use_container_width=True)

            csv_staked_amount = df_staked_amount.to_csv(index=False)
            st.download_button(label="CSV", data=csv_staked_amount, file_name='staked_amount.csv', mime='text/csv')

            # Entry queue chart
            fig_entry_queue = go.Figure()
            fig_entry_queue.add_trace(go.Scatter(x=df_entry_queue['Date'], y=df_entry_queue['entry_queue'], mode='lines', name='Entry Queue'))
            fig_entry_queue.update_layout(
                title='Entry Queue<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                xaxis_title='Date',
                yaxis_title='Entry Queue',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_entry_queue, use_container_width=True)

            csv_entry_queue = df_entry_queue.to_csv(index=False)
            st.download_button(label="CSV", data=csv_entry_queue, file_name='entry_queue.csv', mime='text/csv')

            # Exit queue chart
            fig_exit_queue = go.Figure()
            fig_exit_queue.add_trace(go.Scatter(x=df_exit_queue['Date'], y=df_exit_queue['exit_queue'], mode='lines', name='Exit Queue'))
            fig_exit_queue.update_layout(
                title='Exit Queue<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, beaconcha.in</span>',
                xaxis_title='Date',
                yaxis_title='Exit Queue',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_exit_queue, use_container_width=True)

            csv_exit_queue = df_exit_queue.to_csv(index=False)
            st.download_button(label="CSV", data=csv_exit_queue, file_name='exit_queue.csv', mime='text/csv')

        else:
            st.warning("Data fetching was incomplete. Please try running the app again.")

# Layer 2s Tab ---------------------------------------------------------------------------------
    def tabEthereumL2(self):
        st.header("Ethereum L2 Data")

        time_periods = {'7d': 7, '30d': 30, '90d': 90, '180d': 180, '365d': 365, 'All': None}
        selected_period = st.selectbox("Select Time Period", list(time_periods.keys()), index=4, label_visibility='collapsed')

        with st.spinner('Fetching data...'):
            df_l2_transactions, df_l2_daa_unfiltered, df_l2_transactions_detailed = self.data_instance.fetchEthereumL2Data()

        if df_l2_transactions is not None and not df_l2_transactions.empty and df_l2_daa_unfiltered is not None and not df_l2_daa_unfiltered.empty and df_l2_transactions_detailed is not None and not df_l2_transactions_detailed.empty:
            st.success("Data successfully fetched.")

            columns = ['Arbitrum', 'Base', 'Blast', 'Ethereum', 'Linea', 'Mantle', 'Mode', 'OP Mainnet', 'Polygon zkEVM', 'Scroll', 'zkSync', 'Zora']

            # Filter data based on selected time period
            if time_periods[selected_period] is not None:
                max_date = df_l2_transactions['date'].max()
                min_date = max_date - pd.Timedelta(days=time_periods[selected_period] - 1)
                mask_l2_transactions = (df_l2_transactions['date'] >= min_date) & (df_l2_transactions['date'] <= max_date)
                mask_l2_daa_unfiltered = (df_l2_daa_unfiltered['date'] >= min_date) & (df_l2_daa_unfiltered['date'] <= max_date)
                mask_l2_transactions_detailed = (df_l2_transactions_detailed['date'] >= min_date) & (df_l2_transactions_detailed['date'] <= max_date)
                
                df_l2_transactions = df_l2_transactions.loc[mask_l2_transactions]
                df_l2_daa_unfiltered = df_l2_daa_unfiltered.loc[mask_l2_daa_unfiltered]
                df_l2_transactions_detailed = df_l2_transactions_detailed.loc[mask_l2_transactions_detailed]

                # Create and filter df_l2_normalized here
                df_l2_normalized = df_l2_transactions_detailed[columns].copy()
                df_l2_normalized = df_l2_normalized.div(df_l2_normalized.sum(axis=1), axis=0)
            else:
                # If no time period is selected, create df_l2_normalized from the full dataset
                df_l2_normalized = df_l2_transactions_detailed[columns].copy()
                df_l2_normalized = df_l2_normalized.div(df_l2_normalized.sum(axis=1), axis=0)

            # Stacked transaction count chart
            fig_stacked_l2_txs = go.Figure()
            for column in columns:
                if column != 'Ethereum':
                    fig_stacked_l2_txs.add_trace(go.Bar(x=df_l2_transactions['date'], y=df_l2_transactions[column], name=column))

            fig_stacked_l2_txs.update_layout(
                title='Ethereum L2 Transactions<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis_title='Transaction Count',
                barmode='stack'
            )
            st.plotly_chart(fig_stacked_l2_txs, use_container_width=True)

            csv_l2_transactions = df_l2_transactions[['date'] + columns].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_transactions, file_name='ethereum_l2_transactions.csv', mime='text/csv')

            # Stacked active addresses chart (no filter)
            fig_unfilterd_l2_daa = go.Figure()
            for column in ['Arbitrum', 'Base', 'Blast', 'Linea', 'Mantle', 'Mode', 'Optimism', 'Polygon zkEVM', 'Scroll', 'ZkSync', 'Zora']:
                fig_unfilterd_l2_daa.add_trace(go.Bar(x=df_l2_daa_unfiltered['date'], y=df_l2_daa_unfiltered[column], name=column))

            fig_unfilterd_l2_daa.update_layout(
                title='Ethereum L2 Daily Active Addresses (Unfiltered)<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis_title='Daily Active Addresses',
                barmode='stack'
            )
            st.plotly_chart(fig_unfilterd_l2_daa, use_container_width=True)
            
            csv_l2_daa_unfiltered = df_l2_daa_unfiltered.to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_daa_unfiltered, file_name='ethereum_l2_daa_unfiltered.csv', mime='text/csv')

            # Stacked active addresses chart (filtered) + multi-address share
            df_l2_daa_filtered = df_l2_daa_unfiltered.copy()
            fig_filterd_l2_daa = go.Figure()
            fig_filterd_l2_daa.add_trace(go.Bar(x=df_l2_daa_filtered['date'], y=df_l2_daa_filtered['Single L2 DAA'], name='Single L2s DAAs'))
            fig_filterd_l2_daa.add_trace(go.Bar(x=df_l2_daa_filtered['date'], y=df_l2_daa_filtered['Multi-L2 DAAs'], name='Multi L2 DAAs'))

            df_l2_daa_filtered['multi_share'] = df_l2_daa_filtered['Multi-L2 DAAs'] / (df_l2_daa_filtered['Multi-L2 DAAs'] + df_l2_daa_filtered['Single L2 DAA'])
            fig_filterd_l2_daa.add_trace(go.Scatter(x=df_l2_daa_filtered['date'], y=df_l2_daa_filtered['multi_share'], name='Multi Share', yaxis='y2', line=dict(color='purple', width=2)))

            fig_filterd_l2_daa.update_layout(
                title='Ethereum Single and Multi L2 DAAs<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis=dict(title='Address Count'),
                yaxis2=dict(title='Multi Share', overlaying='y', side='right', range=[0, 1]),
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_filterd_l2_daa, use_container_width=True)
            
            csv_l2_daa_filtered = df_l2_daa_filtered[['date', 'Single L2 DAA', 'Multi-L2 DAAs', 'multi_share']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_daa_filtered, file_name='ethereum_single_multi_l2_daas.csv', mime='text/csv')

            # Individual L2 Txs chart
            fig_detailed_l2_txs = go.Figure()
            for column in columns:
                fig_detailed_l2_txs.add_trace(go.Scatter(x=df_l2_transactions_detailed['date'], y=df_l2_transactions_detailed[column], name=column))

            fig_detailed_l2_txs.update_layout(
                title='Ethereum L2 Transactions (Detailed)<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis_title='Transaction Count',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_detailed_l2_txs, use_container_width=True)

            csv_l2_transactions_detailed = df_l2_transactions_detailed[['date'] + columns].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_transactions_detailed, file_name='ethereum_l2_transactions_detailed.csv', mime='text/csv')

            # New chart: Normalized percentage stacked bar for L2 networks
            columns_reordered = ['Ethereum'] + [col for col in columns if col != 'Ethereum']

            fig_normalized_l2_txs = go.Figure()

            # Add Ethereum first (at the bottom) and color it black
            fig_normalized_l2_txs.add_trace(go.Bar(
                x=df_l2_transactions_detailed['date'],
                y=df_l2_normalized['Ethereum'],
                name='Ethereum',
                marker_color='black'
            ))

            # Add other networks
            for column in columns_reordered[1:]:
                fig_normalized_l2_txs.add_trace(go.Bar(
                    x=df_l2_transactions_detailed['date'],
                    y=df_l2_normalized[column],
                    name=column
                ))

            fig_normalized_l2_txs.update_layout(
                title='Normalized L2 Transaction Share<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis_title='Percentage Share',
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_normalized_l2_txs, use_container_width=True)

            csv_l2_normalized = pd.concat([df_l2_transactions_detailed['date'], df_l2_normalized[columns_reordered]], axis=1).to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_normalized, file_name='ethereum_l2_normalized_transaction_share.csv', mime='text/csv')

            # Summed L2 Txs and share of Ethereum L1 chart
            df_l2_combined_txs_and_percentage = df_l2_transactions_detailed.copy()
            fig_summed_l2_txs = go.Figure()
            fig_summed_l2_txs.add_trace(go.Scatter(x=df_l2_combined_txs_and_percentage['date'], y=df_l2_combined_txs_and_percentage['Combined L2 TXs'], name='Combined L2 TXs', yaxis='y'))
            fig_summed_l2_txs.add_trace(go.Scatter(x=df_l2_combined_txs_and_percentage['date'], y=df_l2_combined_txs_and_percentage['L2 % of Ethereum'], name='L2 % of Ethereum', yaxis='y2'))

            fig_summed_l2_txs.update_layout(
                title='Combined L2 Transactions and L2 % of Ethereum<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis=dict(title='Combined L2 TXs'),
                yaxis2=dict(title='L2 % of Ethereum', overlaying='y', side='right'),
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_summed_l2_txs, use_container_width=True)
            
            csv_l2_combined_txs_and_percentage = df_l2_combined_txs_and_percentage[['date', 'Combined L2 TXs', 'L2 % of Ethereum']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_combined_txs_and_percentage, file_name='combined_l2_transactions_percentage.csv', mime='text/csv')

            # Stacked summed L2 v. Ethereum TX Share
            df_l2_vs_ethereum = df_l2_normalized.copy()
            l2_columns = [col for col in columns if col != 'Ethereum']
            df_l2_vs_ethereum['All L2 TXs'] = df_l2_vs_ethereum[l2_columns].sum(axis=1)
            df_l2_vs_ethereum = df_l2_vs_ethereum[['Ethereum', 'All L2 TXs']]

            fig_l2_vs_ethereum = go.Figure()

            # Add Ethereum first (at the bottom) and color it black
            fig_l2_vs_ethereum.add_trace(go.Bar(
                x=df_l2_transactions_detailed['date'],
                y=df_l2_vs_ethereum['Ethereum'],
                name='Ethereum',
                marker_color='black'
            ))

            # Add All L2 TXs
            fig_l2_vs_ethereum.add_trace(go.Bar(
                x=df_l2_transactions_detailed['date'],
                y=df_l2_vs_ethereum['All L2 TXs'],
                name='All L2 TXs',
                marker_color='rgb(49,130,189)'  # You can change this color if desired
            ))

            fig_l2_vs_ethereum.update_layout(
                title='Normalized Transaction Share: Ethereum vs All L2<br><span style="font-size: 12px; font-style: italic;">Source: Galaxy Research, Dune</span>',
                xaxis_title='Date',
                yaxis_title='Percentage Share',
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_l2_vs_ethereum, use_container_width=True)

            csv_l2_vs_ethereum = pd.concat([df_l2_transactions_detailed['date'], df_l2_vs_ethereum], axis=1).to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_vs_ethereum, file_name='ethereum_vs_all_l2_normalized_transaction_share.csv', mime='text/csv')

        else:
            st.warning("Data fetching was incomplete. Please try running the app again.")

# Run app
App()