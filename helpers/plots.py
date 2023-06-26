# Helper functions and variables for plotting

from pathlib import Path
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

import helpers.helpers as helper
import helpers.power_model as pm

# ========================================
# Helpers
# ========================================
def plot_init(PaperPlot):

    # Select the different output format settings
    if PaperPlot:
        output_format = 'ACM'
    else:
        output_format = 'online'

    if output_format == 'online':
        font_size_px = 14
        linewidth_px = 512
        landscapewidth_px = 654        

        plot_path = Path('plots_online')

    if output_format == 'ACM':
        font_size_pt = 7
        offset = 5 # to compensate for the rounding of unit conversions
        linewidth_pt = 241 - offset  
        landscapewidth_pt = 506 - offset
        
        # 1pt = 1.333px
        font_size_px = int(font_size_pt*1.333)+1
        linewidth_px = int(linewidth_pt*1.333)+1
        landscapewidth_px = int(landscapewidth_pt*1.333)+1

        plot_path = Path('plots_paper')
        
    # Create plot directory if don't exist
    if (plot_path is not None):
        plot_path.mkdir(parents=True, exist_ok=True)

    # Create an dictionary to hold the variables
    plot_var = {
        'output_format' : output_format,
        'font_size_px' : font_size_px,
        'linewidth_px' : linewidth_px,
        'landscapewidth_px' : landscapewidth_px,
        'plot_path' : plot_path
    }
    return plot_var
# ========================================
def plot_save(fig, plot_var):
    if plot_var['output_format'] == 'ACM':
        fig.write_image(str(plot_var['plot_path']/plot_var['plot_name']) + '.pdf')
    if plot_var['output_format'] == 'online':
        fig.write_json(str(plot_var['plot_path']/plot_var['plot_name']) + '.json')
# ========================================
def apply_default_layout(fig, plot_var):
    fig.update_layout(
        title = None,
        font = {"size":plot_var['font_size_px']}
    )
    return fig
# ========================================


# ========================================
# Ploting functions
# ========================================
def average_util(df, PaperPlot=False):

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'average_util'
    start_date = helper.plot_start
    end_date   = helper.plot_end

    # Generate the figure
    fig = px.scatter(
        df, 
        x=df.index, 
        y="average_util",
        labels=dict(average_util="Network utilization (%)")
        )

    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    # .. axes
    fig.update_xaxes(
        range = [start_date,end_date],
        title = 'Date')
    if plot_var['output_format'] == 'online':
        fig.update_xaxes(rangeslider_visible=True)

    fig.update_yaxes(
        range = [0,28],)
    
    # .. sizing and positioning 
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=1.5*plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
            legend=dict(
            )
        )

    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=plot_var['linewidth_px'],
            height=200, 
            margin=dict(l=20, r=0, t=0, b=35),
        )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================
def plot_parallel_link_cdf(parallel_links, PaperPlot=False):

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'parallel_link_cdf'

    # plot the CDF
    fig = px.ecdf(x=parallel_links,ecdfnorm='percent',ecdfmode="complementary")

    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    # .. axes
    fig.update_xaxes(
        title = 'Number of links connecting two hosts',
        tickmode = 'array',
        tickvals = [1, 2, 4, 10],
    )
    fig.update_yaxes(
        title = 'CCDF of links (%)',
        tickmode = 'array',
        tickvals = [100-0, 100-45, 100-68, 100-89],
    )

    # .. sizing and positioning 
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=1.5*plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
            legend=dict(
            )
        )

    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=plot_var['linewidth_px'],
            height=160, 
            margin=dict(l=20, r=0, t=0, b=35),
        )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================
def plot_sleeping_potential(df, PaperPlot=False):

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'sleeping_potential'

    # Per time bin without aggregation
    fig = px.scatter(df, 
                    x='bin-time', 
                    y="potential_savings_%",
                    marginal_y="histogram",
                    #  marginal_y="box",
                        labels={
                            "bin-time": "Time of day",
                            "potential_savings_%": "Links we can put to sleep (%)",
                        },
    )

    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    fig.update_traces(marker=dict(opacity=0.01,),
                    selector=dict(mode='markers'))

    # .. axes
    # Make the xaxis display the time of the day
    fig.update_xaxes(
        tickformat="%H\n%M",
        tickformatstops=[
            dict(dtickrange=[3600000, 86400000], value="%H:%M")]  # range is 1 hour to 24 hours
    )
    fig.update_yaxes(
        range = [40,65],
    )

    # .. sizing and positioning 
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=1.5*plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
            legend=dict(
            )
        )

    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=plot_var['linewidth_px'],
            height=200, 
            margin=dict(l=20, r=0, t=0, b=35),
        )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================
def plot_rate_adaptation_potential(df, PaperPlot=False):

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'plot_RA'


    # Per time bin without aggregation
    fig = px.scatter(df, 
                    x='bin-time', 
                    y=["10_ratio", "25_ratio"],
                    marginal_y="histogram",
                    #  marginal_y="box",
                    labels={
                        "bin-time": "Time of day",
                        "10_ratio": "Links with load <= 10Gbps (%)",
                        "25_ratio": "Links loaded <= 25Gbps (%)"
                    },
    )

    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    fig.update_traces(marker=dict(opacity=0.01,),
                    selector=dict(mode='markers'))

    # .. axes
    # Make the xaxis display the time of the day
    fig.update_xaxes(
        tickformat="%H\n%M",
        tickformatstops=[
            dict(dtickrange=[3600000, 86400000], value="%H:%M")]  # range is 1 hour to 24 hours
    )
    fig.update_yaxes(
        range = [10,50],
    )
    fig.update_yaxes(
        title = 'Links we can down-rate (%)',
        col=1
    )

    # .. legend
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=''
        )
    )
    # .. overwrite the trace name
    fig['data'][0]['name'] = 'down to 10G'
    fig['data'][2]['name'] = 'down to 25G'

    # .. sizing and positioning 
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=1.5*plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
        )

    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=plot_var['linewidth_px'],
            height=200, 
            margin=dict(l=20, r=0, t=0, b=35),
        )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================
def _prep_plot_compare_strategies(max_load, max_links, datapoints):

    # Load the power model
    port_power, idle_power = pm.power_model()

    ##
    # Trafic load (x-axis)
    # .. We do not care about where the traffic goes 
    # .. It is as is we consider the traffic sent between two directly
    # connected hosts
    ## 
    load = np.linspace(0, max_load, datapoints) # in Gbps

    ## 
    # Baseline: idle power 
    ##
    idle = idle_power*np.ones(datapoints)

    ## 
    # Sleeping 
    # .. that is, minimizing the number of links used
    # .. - Each link is set at 100G
    ## 
    sleeping = []
    for l in load:
        req_links = np.ceil(l/100)
        # assumes linearity of the dynamic power
        power = (
            idle_power + 
            req_links*port_power[100]['static_power'] + 
            l*port_power[100]['dynamic_power'] 
        )
        sleeping.append(power)

    ## 
    # Naive load balancing 
    # .. that is, spreading the load but leaving port set at max
    # .. - Each link is set at 100G
    # .. - Consider 10 links (to get to the same 1T range)
    ## 
    load_balancing = []
    for l in load:
        req_links = max_links
        # assumes linearity of the dynamic power
        power = (
            idle_power + 
            req_links*port_power[100]['static_power'] + 
            l*port_power[100]['dynamic_power'] 
        )
        load_balancing.append(power)

    ## 
    # Rate adaptation 
    # .. that is, spreading the load but adjust required rate per link
    # .. - Each link is set to the same config
    # .. - Consider 10 links (to get to the same 1T range)
    ## 
    rate_adaptation = []
    for l in load:
        req_links = max_links
        # keeps ports at low rate for as long as possible
        req_rate = helper.capacity_bounds(l/req_links)
        # assumes linearity of the dynamic power
        power = (
            idle_power + 
            req_links*port_power[req_rate]['static_power'] + 
            l*port_power[req_rate]['dynamic_power'] 
        )
        rate_adaptation.append(power)


    ## 
    # Optimal rate adaptation 
    # .. that is, spreading the load but adjust required rate per link
    # .. - Each link is set optimally to best static power
    # .. - Consider 10 links (to get to the same 1T range)
    ## 

    df = helper.all_port_configs(max_links)
    opt_rate_adaptation = []
    for l in load:
        # get the optimal static power config
        static_power = df.loc[df['max_capacity'] >= l].iloc[0]['power']
        # assumes linearity of the dynamic power
        dynamic_power = 0
        l_left = l
        for link in range(max_links):
            # .. link rate
            rate = df.loc[df['max_capacity'] >= l].iloc[0][link]
            # .. load on that link
            l_link = min(l_left, rate)
            # .. corresponding power
            dynamic_power += l_link*port_power[rate]['dynamic_power']
            # .. remaining load
            l_left = l_left - l_link
            # .. exit 
            if l_left <= 0:
                break

        power = (
            idle_power + 
            static_power + 
            dynamic_power
        )
        opt_rate_adaptation.append(power)

    ## 
    # Optimal rate adaptation + Sleeping 
    # .. that is, spreading the load but adjust required rate per link
    # .. - Each link is set optimally to best static power
    # .. - Consider 10 links (to get to the same 1T range)
    # .. - Allow config that turn links off
    ## 

    df = helper.all_port_configs(max_links, allow_sleeping=True)
    opt_rate_adaptation_plus_sleep = []
    for l in load:
        # get the optimal static power config
        static_power = df.loc[df['max_capacity'] >= l].iloc[0]['power']
        # assumes linearity of the dynamic power
        dynamic_power = 0
        l_left = l
        for link in range(max_links):
            # .. link rate
            rate = df.loc[df['max_capacity'] >= l].iloc[0][link]
            # .. load on that link
            l_link = min(l_left, rate)
            # .. corresponding power
            dynamic_power += l_link*port_power[rate]['dynamic_power']
            # .. remaining load
            l_left = l_left - l_link
            # .. exit 
            if l_left <= 0:
                break

        power = (
            idle_power + 
            static_power + 
            dynamic_power
        )
        opt_rate_adaptation_plus_sleep.append(power)

    ## 
    # Plot
    ## 
    fig = go.Figure()
    traces = []

    # Add traces
    traces.append(go.Scatter(x=load, y=load_balancing,
                        mode='lines',
                        name='No adaptation',
                        line = dict(color='red'),
                        legendgroup='a'))
    traces.append(go.Scatter(x=load, y=sleeping,
                        mode='lines',
                        name='Sleeping',
                        line = dict(color='purple'),
                        legendgroup='b'))
    traces.append(go.Scatter(x=load, y=rate_adaptation,
                        mode='lines',
                        name='Uni. Down-rating',
                        line = dict(color='orange'),
                        legendgroup='c'))
    traces.append(go.Scatter(x=load, y=opt_rate_adaptation,
                        mode='lines',
                        name='Opt. Down-rating',
                        line = dict(color='SeaGreen'),
                        legendgroup='d'))
    traces.append(go.Scatter(x=load, y=opt_rate_adaptation_plus_sleep,
                        mode='lines',
                        name='Opt. Rate Adaptation',
                        line = dict(color='chartreuse'),
                        legendgroup='e'))
    traces.append(go.Scatter(x=load, y=idle,
                        mode='lines',
                        name='Idle power',
                        line = dict(
                            color='royalblue', 
                            width=4, 
                            dash='dash'),
                        legendgroup='f'))

    fig.add_traces(traces)

    return fig, traces

def plot_compare_strategies(PaperPlot=False):
    # Comparison of adaptation strategies
    # [Subplot version]

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'plot_model_mixed'
    max_loads = [100, 200, 400]  # Gbps 
    # .. set links maximum we consider between the two endpoints
    max_links = [int(np.ceil(l/100)) for l in max_loads]
    label_subplots = ('1 link', '2 links', '4 links')
    numb_subplots = len(max_loads)
    # .. set a consistent number of datapoints for ploting
    datapoints = 101

    # Initialize the figure
    fig = make_subplots(
        rows=1, 
        cols=numb_subplots, 
        subplot_titles=label_subplots,
    )

    # Add all traces
    for i in range(numb_subplots):
        max_load = max_loads[i]
        max_link = max_links[i]
        single_fig, traces = _prep_plot_compare_strategies(max_load, max_link, datapoints)

        for t in traces:
            fig.add_trace(t, row=1, col=i+1)


    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    # .. axes
    fig.update_xaxes(
        title = {
            'text':'Load between two routers [Gbps]',
        }, col=2
    )
    fig.update_yaxes(
        title = {
            'text':'Total power [W]',
        }, col=1
    )

    # .. sizing and positioning 
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=2*plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
            legend=dict(
            )
        )
    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=plot_var['landscapewidth_px'],
            height=180, 
            margin=dict(l=20, r=0, t=20, b=35),
        )

    # .. polish the legend
    # Remove duplicate legend entries
    # -> assumed that we keep all 6 in the last plot
    for i in range(len(fig['data'])-6):
        fig['data'][i]['showlegend'] = False
    fig.update_layout(
        legend=dict(
            font=dict(size=0.9*plot_var['font_size_px']),
            tracegroupgap=0
            # title='Configuration strategy',
        )
    )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================
def plot_dynamic_power(PaperPlot=False):

    # Set plot variables
    plot_var = plot_init(PaperPlot)
    plot_var['plot_name'] = 'plot_P=f(U)'

    # Load data
    Gbps, power = pm.load_exp_data()

    # Generate figure
    fig   = px.scatter(x=Gbps, y=power, trendline="ols")
    model = px.get_trendline_results(fig)
    alpha = model.iloc[0]["px_fit_results"].params[0]
    beta  = model.iloc[0]["px_fit_results"].params[1]

    # Adjust layout
    # .. default things
    fig = apply_default_layout(fig, plot_var)

    # .. anotation
    fig.data[1].line.color = 'red'
    reg_output = 'y = {:.02f} x + {:.0f}'.format(beta, alpha)
    fig.add_annotation(
        x=60, 
        y=140,
        ax=0,
        ay=-34,
        text=reg_output,
        showarrow=True,
        arrowhead=0,
        bgcolor="#ffffff",
        borderpad=4,
    )

    # .. axes
    fig.update_xaxes(
        title = {
            'text':'Load per port [Gbps]',
        }
    )
    fig.update_yaxes(
        title = {
            'text':'Total power [W]',
        }
    )

    # .. sizing and positioning     
    if plot_var['output_format'] == 'online':
        fig.update_layout(
            width=plot_var['linewidth_px'],
            height=400, 
            margin=dict(l=40, r=0, t=0, b=35),
        )

    if plot_var['output_format'] == 'ACM':
        fig.update_layout(
            width=0.8*plot_var['linewidth_px'],
            height=130, 
            margin=dict(l=20, r=0, t=0, b=35),
        )

    # Show plot
    fig.show()

    # Save plot
    plot_save(fig, plot_var)
# ========================================