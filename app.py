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
        st.title("Hello World!")

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
            df2 = self.data_instance.fetchStakedAmount()
            df3 = self.data_instance.fetchEntryQueue()
            df4 = self.data_instance.fetchExitQueue()
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
            and df2 is not None
            and not df2.empty
            and df3 is not None
            and not df3.empty
            and df4 is not None
            and not df4.empty
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
                latest_staked_amount = df2['staked_amount'].iloc[-1] / 1_000_000
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
                mask2 = (df2['Date'] >= min_date) & (df2['Date'] <= max_date)
                mask3 = (df3['Date'] >= min_date) & (df3['Date'] <= max_date)
                mask4 = (df4['Date'] >= min_date) & (df4['Date'] <= max_date)
                mask_staking_apy = (df_staking_apy['Date'] >= min_date) & (df_staking_apy['Date'] <= max_date)
                df_entry_wait = df_entry_wait.loc[mask_entry_wait]
                df_exit_wait = df_exit_wait.loc[mask_exit_wait]
                df_validators_churn = df_validators_churn.loc[mask_validators_churn]
                df_apr = df_apr.loc[mask_apr]
                df2 = df2.loc[mask2]
                df3 = df3.loc[mask3]
                df4 = df4.loc[mask4]
                df_staking_apy = df_staking_apy.loc[mask_staking_apy]

            # Side by side entry/exit wait charts
            col1, col2 = st.columns(2)
            with col1:
                fig_entry_wait = go.Figure()
                fig_entry_wait.add_trace(go.Scatter(x=df_entry_wait['Date'], y=df_entry_wait['entry_wait'], mode='lines', name='Entry Wait'))
                fig_entry_wait.update_layout(
                    title='Entry Wait (Days)<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
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
                    title='Exit Wait (Days)<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
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
                title='Staking APY Breakdown<br><span style="font-size: 12px; font-style: italic;">Source: Beaconcha.in, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='APY (%)',
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_staking_apy, use_container_width=True)

            csv_staking_apy = df_staking_apy[['Date', 'Yearly Issuance APY', 'Yearly MEV APY', 'Yearly TIPS APY']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_staking_apy, file_name='staking_apy_breakdown.csv', mime='text/csv')

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
                    name='Churn',
                    yaxis='y2',
                )
            )
            fig_validators_churn.update_layout(
                title='Validators and Churn<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Validators',
                yaxis2=dict(title='Churn', side='right', overlaying='y'),
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_validators_churn, use_container_width=True)

            csv_validators_churn = df_validators_churn.to_csv(index=False)
            st.download_button(label="CSV", data=csv_validators_churn, file_name='validators_churn.csv', mime='text/csv')

            # Staked ETH amount and % of total ETH staked
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df2['Date'], y=df2['staked_amount'], mode='lines', name='Staked Amount'))
            fig2.add_trace(go.Scatter(x=df2['Date'], y=df2['staked_percent'], mode='lines', name='Staked Percent', yaxis='y2'))
            fig2.update_layout(
                title='Staked Amount and Percentage<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Staked Amount',
                yaxis2=dict(title='Staked Percent', side='right', overlaying='y'),
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig2, use_container_width=True)

            csv_staked_amount = df2.to_csv(index=False)
            st.download_button(label="CSV", data=csv_staked_amount, file_name='staked_amount.csv', mime='text/csv')

            # Entry queue chart
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df3['Date'], y=df3['entry_queue'], mode='lines', name='Entry Queue'))
            fig3.update_layout(
                title='Entry Queue<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Entry Queue',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig3, use_container_width=True)

            csv_entry_queue = df3.to_csv(index=False)
            st.download_button(label="CSV", data=csv_entry_queue, file_name='entry_queue.csv', mime='text/csv')

            # Exit queue chart
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=df4['Date'], y=df4['exit_queue'], mode='lines', name='Exit Queue'))
            fig4.update_layout(
                title='Exit Queue<br><span style="font-size: 12px; font-style: italic;">Source: beaconcha.in, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Exit Queue',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig4, use_container_width=True)

            csv_exit_queue = df4.to_csv(index=False)
            st.download_button(label="CSV", data=csv_exit_queue, file_name='exit_queue.csv', mime='text/csv')

        else:
            st.warning("Data fetching was incomplete. Please try running the app again.")

# Layer 2s Tab ---------------------------------------------------------------------------------
    def tabEthereumL2(self):
        st.header("Ethereum L2 Data")

        time_periods = {'7d': 7, '30d': 30, '90d': 90, '180d': 180, '365d': 365, 'All': None}
        selected_period = st.selectbox("Select Time Period", list(time_periods.keys()), index=1, label_visibility='collapsed')

        with st.spinner('Fetching data...'):
            df_l2_1, df_l2_2, df_l2_3 = self.data_instance.fetchEthereumL2Data()

        if df_l2_1 is not None and not df_l2_1.empty and df_l2_2 is not None and not df_l2_2.empty and df_l2_3 is not None and not df_l2_3.empty:
            st.success("Data successfully fetched.")

            # Filter data based on selected time period
            if time_periods[selected_period] is not None:
                max_date = df_l2_1['date'].max()
                min_date = max_date - pd.Timedelta(days=time_periods[selected_period] - 1)
                mask_l2_1 = (df_l2_1['date'] >= min_date) & (df_l2_1['date'] <= max_date)
                mask_l2_2 = (df_l2_2['date'] >= min_date) & (df_l2_2['date'] <= max_date)
                mask_l2_3 = (df_l2_3['date'] >= min_date) & (df_l2_3['date'] <= max_date)
                df_l2_1 = df_l2_1.loc[mask_l2_1]
                df_l2_2 = df_l2_2.loc[mask_l2_2]
                df_l2_3 = df_l2_3.loc[mask_l2_3]

            fig_l2_1 = go.Figure()
            columns = ['Arbitrum', 'Base', 'Blast', 'Linea', 'Mantle', 'Mode', 'OP Mainnet', 'Polygon zkEVM', 'Scroll', 'zkSync', 'Zora']
            for column in columns:
                fig_l2_1.add_trace(go.Bar(x=df_l2_1['date'], y=df_l2_1[column], name=column))

            fig_l2_1.update_layout(
                title='Ethereum L2 Transactions<br><span style="font-size: 12px; font-style: italic;">Source: Dune, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Transaction Count',
                barmode='stack'
            )
            st.plotly_chart(fig_l2_1, use_container_width=True)

            csv_l2_1 = df_l2_1[['date'] + columns].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_1, file_name='ethereum_l2_transactions.csv', mime='text/csv')

            fig_l2_2 = go.Figure()
            for column in ['Arbitrum', 'Base', 'Blast', 'Linea', 'Mantle', 'Mode', 'Optimism', 'Polygon zkEVM', 'Scroll', 'ZkSync', 'Zora']:
                fig_l2_2.add_trace(go.Bar(x=df_l2_2['date'], y=df_l2_2[column], name=column))

            fig_l2_2.update_layout(
                title='Ethereum L2 Daily Active Addresses (Unfiltered)<br><span style="font-size: 12px; font-style: italic;">Source: Dune, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Daily Active Addresses',
                barmode='stack'
            )
            st.plotly_chart(fig_l2_2, use_container_width=True)
            
            csv_l2_2 = df_l2_2.to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_2, file_name='ethereum_l2_daa_unfiltered.csv', mime='text/csv')

            fig_l2_3 = go.Figure()
            fig_l2_3.add_trace(go.Bar(x=df_l2_2['date'], y=df_l2_2['Single L2 DAA'], name='Single L2s DAAs'))
            fig_l2_3.add_trace(go.Bar(x=df_l2_2['date'], y=df_l2_2['Multi-L2 DAAs'], name='Multi L2 DAAs'))

            df_l2_2['multi_share'] = df_l2_2['Multi-L2 DAAs'] / (df_l2_2['Multi-L2 DAAs'] + df_l2_2['Single L2 DAA'])
            fig_l2_3.add_trace(go.Scatter(x=df_l2_2['date'], y=df_l2_2['multi_share'], name='Multi Share', yaxis='y2', line=dict(color='purple', width=2)))

            fig_l2_3.update_layout(
                title='Ethereum Single and Multi L2 DAAs<br><span style="font-size: 12px; font-style: italic;">Source: Dune, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis=dict(title='Address Count'),
                yaxis2=dict(title='Multi Share', overlaying='y', side='right', range=[0, 1]),
                barmode='stack',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_l2_3, use_container_width=True)
            
            csv_l2_3 = df_l2_2[['date', 'Single L2 DAA', 'Multi-L2 DAAs', 'multi_share']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_3, file_name='ethereum_single_multi_l2_daas.csv', mime='text/csv')

            # New chart for df_l2_3 (line chart)
            fig_l2_4 = go.Figure()
            columns = ['Arbitrum', 'Base', 'Blast', 'Linea', 'Mantle', 'Mode', 'OP Mainnet', 'Polygon zkEVM', 'Scroll', 'zkSync', 'Zora']
            for column in columns:
                fig_l2_4.add_trace(go.Scatter(x=df_l2_3['date'], y=df_l2_3[column], name=column))

            fig_l2_4.update_layout(
                title='Ethereum L2 Transactions (Detailed)<br><span style="font-size: 12px; font-style: italic;">Source: Dune, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis_title='Transaction Count',
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_l2_4, use_container_width=True)

            csv_l2_4 = df_l2_3[['date'] + columns].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_4, file_name='ethereum_l2_transactions_detailed.csv', mime='text/csv')

            # New chart for df_l2_3 (combined chart)
            fig_l2_5 = go.Figure()
            fig_l2_5.add_trace(go.Scatter(x=df_l2_3['date'], y=df_l2_3['Combined L2 TXs'], name='Combined L2 TXs', yaxis='y'))
            fig_l2_5.add_trace(go.Scatter(x=df_l2_3['date'], y=df_l2_3['L2 % of Ethereum'], name='L2 % of Ethereum', yaxis='y2'))

            fig_l2_5.update_layout(
                title='Combined L2 Transactions and L2 % of Ethereum<br><span style="font-size: 12px; font-style: italic;">Source: Dune, Galaxy Research</span>',
                xaxis_title='Date',
                yaxis=dict(title='Combined L2 TXs'),
                yaxis2=dict(title='L2 % of Ethereum', overlaying='y', side='right'),
                legend=dict(x=0, y=1, orientation='h')
            )
            st.plotly_chart(fig_l2_5, use_container_width=True)
            
            csv_l2_5 = df_l2_3[['date', 'Combined L2 TXs', 'L2 % of Ethereum']].to_csv(index=False)
            st.download_button(label="CSV", data=csv_l2_5, file_name='combined_l2_transactions_percentage.csv', mime='text/csv')

        else:
            st.warning("Data fetching was incomplete. Please try running the app again.")

# Run app
App()