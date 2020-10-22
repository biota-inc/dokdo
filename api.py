from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skbio as sb

import qiime2
from qiime2 import Artifact
from qiime2 import Metadata
from qiime2 import Visualization



def ancom_volcano_plot(ancom, figsize=None, ax=None):
    """
    This method creates an ANCOM volcano plot.

    Parameters
    ----------
    ancom : str
        Path to the visualization file from the 'qiime composition ancom' 
        command.
    figsize : tuple of float, optional
        Width, height in inches.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    """
    t = TemporaryDirectory()
    Visualization.load(ancom).export_data(t.name)
    df = pd.read_table(f'{t.name}/data.tsv')
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(df.clr, df.W, s=80, c='black', alpha=0.5)
    ax.set_xlabel('clr')
    ax.set_ylabel('W')



def alpha_diversity_plot(significance, where, figsize=None, ax=None):
    """
    This method creates an alpha diversity plot.

    Parameters
    ----------
    significance : str
        Path to the visualization file from the 'qiime diversity 
        alpha-group-significance' command.
    where : str
        Column name to be used for the x-axis.
    figsize : tuple of float, optional
        Width, height in inches.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    """
    t = TemporaryDirectory()
    Visualization.load(significance).export_data(t.name)
    df = Metadata.load(f'{t.name}/metadata.tsv').to_dataframe()
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    metric = df.columns[-1]
    boxprops = dict(color='white', edgecolor='black')
    sns.boxplot(x=where, y=metric, data=df, ax=ax, boxprops=boxprops)



def read_quality_plot(demux, strand='forward', figsize=None, ax=None):
    """
    This method creates a read quality plot.

    Parameters
    ----------
    demux : str
        Path to the visualization file from the 'qiime demux summarize' 
        command.
    strand : str, default: 'forward'
        Read strand to be displayed (either 'forward' or 'reverse').
    figsize : tuple of float, optional
        Width, height in inches.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    """
    t = TemporaryDirectory()
    Visualization.load(demux).export_data(t.name)

    l = ['forward', 'reverse']
    if strand not in l:
        raise ValueError(f"Strand should be one of the following: {l}")

    df = pd.read_table(f'{t.name}/{strand}-seven-number-summaries.tsv',
                       index_col=0, skiprows=[1])
    df = pd.melt(df.reset_index(), id_vars=['index'])
    df['variable'] = df['variable'].astype('int64')
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    sns.boxplot(x='variable', y='value', data=df, ax=ax, fliersize=0,
                boxprops=dict(color='white', edgecolor='black'),
                medianprops=dict(color='red'),
                whiskerprops=dict(linestyle=':'))

    ax.set_ylim([0, 45])
    ax.set_xlabel('Sequence base')
    ax.set_ylabel('Quality score')
    a = np.arange(df['variable'].min(), df['variable'].max(), 20)
    ax.set_xticks(a)
    ax.set_xticklabels(a)













def alpha_rarefaction_plot(rarefaction,
                           hue='sample-id',
                           metric='shannon',
                           ax=None,
                           figsize=None,
                           show_legend=False,
                           legend_loc='best',
                           legend_ncol=1):
    """
    This method creates an alpha rarefaction plot.

    Parameters
    ----------
    rarefaction : str or qiime2.sdk.result.Visualization
        Visualization file or object from alpha rarefaction.
    hue : str, default: 'sample-id'
        Grouping variable that will produce lines with different colors.
    metric : str, default: 'shannon'
        Diversity metric ('shannon', 'observed_features', or 'faith_pd').
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    show_legend : bool, default: False
        Show the legend.
    legend_loc : str, default: 'best'
        Legend location specified as in matplotlib.pyplot.legend.
    legend_ncol : int, default: 1
        The number of columns that the legend has.
    """
    t = TemporaryDirectory()

    if isinstance(rarefaction, qiime2.sdk.result.Visualization):
        fn = f'{t.name}/alpha-rarefaction.qzv'
        rarefaction.save(fn)
        rarefaction = fn

    Visualization.load(rarefaction).export_data(t.name)

    l = ['observed_features', 'faith_pd', 'shannon']
    if metric not in l:
        raise ValueError(f"Metric should be one of the following: {l}")

    df = pd.read_csv(f'{t.name}/{metric}.csv', index_col=0)

    metadata_columns = [x for x in df.columns if 'iter' not in x]

    df = pd.melt(df.reset_index(), id_vars=['sample-id'] + metadata_columns)

    df['variable'] = df['variable'].str.split('_').str[0].str.replace(
                         'depth-', '').astype(int)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    sns.lineplot(x='variable',
                 y='value',
                 data=df,
                 hue=hue,
                 ax=ax,
                 err_style='bars',
                 sort=False)

    ax.set_xlabel('Sequencing depth')
    ax.set_ylabel(metric)

    # Control the legend.
    if not hue:
        pass
    elif show_legend:
        ax.legend(loc=legend_loc, ncol=legend_ncol)
    else:
        ax.get_legend().remove()





















def taxa_abundance_bar_plot(taxa,
                            level=1,
                            by=[],
                            ax=None,
                            figsize=None,
                            width=0.8,
                            count=0,
                            exclude_samples={},
                            exclude_taxa=[],
                            show_legend=False,
                            legend_short=False,
                            legend_loc='best',
                            sort_by_names=False,
                            colors=[],
                            hide_xlabels=False,
                            hide_ylabels=False,
                            label_columns=[],
                            orders={},
                            sample_names=[],
                            csv_file=None,
                            xlabels=None):
    """
    This method creates a taxa abundance plot.

    Parameters
    ----------
    taxa : str
        Path to the visualization file from the 'qiime taxa barplot'.
    level : int
        Taxonomic level at which the features should be collapsed.
    by : list of str
        Column name(s) to be used for sorting the samples. Using 'index' will 
        sort the samples by their name, in addition to other column name(s) 
        that may have been provided. If multiple items are provided, sorting 
        will occur by the order of the items.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    width : float
        The width of the bars.
    count : int, default: 0
        The number of taxa to display. When 0, display all.
    exclude_samples : dict
        Dictionary of column name(s) to list(s) of column value(s) to use to 
        exclude samples.
    exclude_taxa : list
        The taxa names to be excluded when matched. Case insenstivie.
    show_legend : bool, default: False
        Show the legend.
    legend_short : bool
        If true, only display the smallest taxa rank in the legend.
    legend_loc : str, default: 'best'
        Legend location specified as in matplotlib.pyplot.legend.
    sort_by_names : bool
        If true, sort the columns (i.e. species) to be displayed by name.
    colors : list
        The bar colors.
    hide_xlabels : bool, default: False
        Hide all the x-axis labels.
    hide_ylabels : bool, default: False
        Hide all the y-axis labels.
    label_columns : list
        The column names to be used as the x-axis labels.
    orders : dict
        Dictionary of {column1: [element1, element2, ...], column2: 
        [element1, element2...], ...} to indicate the order of items. Used to 
        sort the sampels by the user-specified order instead of ordering 
        numerically or alphabetically.
    sample_names : list
        List of sample IDs to be included.
    csv_file : str
        Path of the .csv file to output the dataframe to.
    xlabels : list, optional
        List of the x-axis labels.
    """
    t = TemporaryDirectory()
    Visualization.load(taxa).export_data(t.name)
    df = pd.read_csv(f'{t.name}/level-{level}.csv', index_col=0)

    # If provided, sort the samples by the user-specified order instead of 
    # ordering numerically or alphabetically. To do this, we will first add a 
    # new temporary column filled with the indicies of the user-provided 
    # list. This column will be used for sorting the samples later instead of 
    # the original column. After sorting, the new column will be dropped from 
    # the dataframe and the original column will replace its place.
    for k, v in orders.items():
        u = df[k].unique().tolist()

        if set(u) != set(v):
            message = (f"Target values {u} not matched with user-provided "
                       f"values {v} for metadata column `{k}`")
            raise ValueError(message)

        l = [x for x in range(len(v))]
        d = dict(zip(v, l))
        df.rename(columns={k: f'@{k}'}, inplace=True)
        df[k] = df[f'@{k}'].map(d)

    # If provided, sort the samples for display in the x-axis.
    if by:
        df = df.sort_values(by=by)

    # If sorting was performed by the user-specified order, remove the 
    # temporary columns and then bring back the original column.
    for k in orders:
        df.drop(columns=[k], inplace=True)
        df.rename(columns={f'@{k}': k}, inplace=True)

    # If provided, exclude the specified samples.
    if exclude_samples:
        for x in exclude_samples:
            for y in exclude_samples[x]:
                df = df[df[x] != y]

    # If provided, exclude the specified taxa.
    if exclude_taxa:
        dropped = []
        for tax in exclude_taxa:
            for col in df.columns:
                if tax.lower() in col.lower():
                    dropped.append(col)
        dropped = list(set(dropped))
        df = df.drop(columns=dropped)

    # If provided, only include the specified samples.
    if sample_names:
        df = df.loc[sample_names]

    # Remove the metadata columns.
    dropped = []
    for column in df.columns:
        if 'Unassigned' in column:
            continue
        elif '__' in column:
            continue
        else:
            dropped.append(column)

    mf = df[dropped]
    mf = mf.assign(**{'sample-id': mf.index})
    df = df.drop(columns=dropped)




    # Convert counts to proportions.
    df = df.div(df.sum(axis=1), axis=0)

    # Sort the columns (i.e. species) by their mean abundance.
    df = df.loc[:, df.mean().sort_values(ascending=False).index]

    # If provided, collapse extra species to the Other column.
    if count is not 0:
        other = df.iloc[:, count-1:].sum(axis=1)
        df = df.iloc[:, :count-1]
        df['Other'] = other

    if sort_by_names:
        df = df.reindex(sorted(df.columns), axis=1)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    if show_legend and legend_short:
        def f(s):
            ranks = s.split(';')
            for rank in reversed(ranks):
                if rank != '__':
                    x = rank
                    break
            return x
        df.columns = [f(x) for x in df.columns]

    if colors:
        c = colors
    else:
        c = plt.cm.get_cmap('Accent').colors


    df.plot.bar(stacked=True,
                legend=False,
                ax=ax,
                width=width,
                color=c)


    ax.set_xlabel('')
    ax.set_ylabel('Relative frequency')


    # Control the x-axis labels.
    if hide_xlabels:
        ax.set_xticks([])
    elif label_columns:
        f = lambda row: ' : '.join(row.values.astype(str))
        new_labels = mf[label_columns].apply(f, axis=1)
        ax.set_xticklabels(new_labels)
    else:
        pass

    # Control the y-axis labels.
    if hide_ylabels:
        ax.set_ylabel('')
        ax.set_yticks([])

    # Control the legend.
    if show_legend:
        ax.legend(loc=legend_loc)

    # If provided, output the dataframe as a .csv file.
    if csv_file is not None:
        df.to_csv(csv_file)

    if xlabels is not None:
        xtexts = [x.get_text() for x in ax.get_xticklabels()]
        if len(xtexts) != len(xlabels):
            m = f"Expected {len(xtexts)} items, but found {len(xlabels)}"
            raise ValueError(m)
        ax.set_xticklabels(xlabels)



















def taxa_abundance_box_plot(taxa,
                            level=1,
                            by=[],
                            ax=None,
                            figsize=None,
                            width=0.8,
                            count=0,
                            exclude_samples={},
                            exclude_taxa=[],
                            show_legend=False,
                            legend_short=False,
                            legend_loc='best',
                            sort_by_names=False,
                            colors=[],
                            hide_xlabels=False,
                            hide_ylabels=False,
                            label_columns=[],
                            orders={},
                            sample_names=[],
                            csv_file=None,
                            size=5,
                            xlabels=None,
                            log_scale=False):
    """
    This method creates a taxa abundance box plot.

    Parameters
    ----------
    taxa : str
        Path to the visualization file from the 'qiime taxa barplot'.
    level : int
        Taxonomic level at which the features should be collapsed.
    by : list of str
        Column name(s) to be used for sorting the samples. Using 'index' will 
        sort the samples by their name, in addition to other column name(s) 
        that may have been provided. If multiple items are provided, sorting 
        will occur by the order of the items.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    width : float
        The width of the bars.
    count : int, default: 0
        The number of taxa to display. When 0, display all.
    exclude_samples : dict
        Dictionary of column name(s) to list(s) of column value(s) to use to 
        exclude samples.
    exclude_taxa : list
        The taxa names to be excluded when matched. Case insenstivie.
    show_legend : bool, default: False
        Show the legend.
    legend_short : bool
        If true, only display the smallest taxa rank in the legend.
    legend_loc : str, default: 'best'
        Legend location specified as in matplotlib.pyplot.legend.
    sort_by_names : bool
        If true, sort the columns (i.e. species) to be displayed by name.
    colors : list
        The bar colors.
    hide_xlabels : bool, default: False
        Hide all the x-axis labels.
    hide_ylabels : bool, default: False
        Hide all the y-axis labels.
    label_columns : list
        The column names to be used as the x-axis labels.
    orders : dict
        Dictionary of {column1: [element1, element2, ...], column2: 
        [element1, element2...], ...} to indicate the order of items. Used to 
        sort the sampels by the user-specified order instead of ordering 
        numerically or alphabetically.
    sample_names : list
        List of sample IDs to be included.
    csv_file : str
        Path of the .csv file to output the dataframe to.
    size : float, default: 5.0
        Radius of the markers, in points.
    xlabels : list, optional
        List of the x-axis labels.
    log_scale : bool, default: False
        Draw the y-axis in log scale.
    """
    t = TemporaryDirectory()
    Visualization.load(taxa).export_data(t.name)
    df = pd.read_csv(f'{t.name}/level-{level}.csv', index_col=0)

    # If provided, sort the samples by the user-specified order instead of 
    # ordering numerically or alphabetically. To do this, we will first add a 
    # new temporary column filled with the indicies of the user-provided 
    # list. This column will be used for sorting the samples later instead of 
    # the original column. After sorting, the new column will be dropped from 
    # the dataframe and the original column will replace its place.
    for k, v in orders.items():
        u = df[k].unique().tolist()

        if set(u) != set(v):
            message = (f"Target values {u} not matched with user-provided "
                       f"values {v} for metadata column `{k}`")
            raise ValueError(message)

        l = [x for x in range(len(v))]
        d = dict(zip(v, l))
        df.rename(columns={k: f'@{k}'}, inplace=True)
        df[k] = df[f'@{k}'].map(d)

    # If provided, sort the samples for display in the x-axis.
    if by:
        df = df.sort_values(by=by)

    # If sorting was performed by the user-specified order, remove the 
    # temporary columns and then bring back the original column.
    for k in orders:
        df.drop(columns=[k], inplace=True)
        df.rename(columns={f'@{k}': k}, inplace=True)

    # If provided, exclude the specified samples.
    if exclude_samples:
        for x in exclude_samples:
            for y in exclude_samples[x]:
                df = df[df[x] != y]

    # If provided, exclude the specified taxa.
    if exclude_taxa:
        dropped = []
        for tax in exclude_taxa:
            for col in df.columns:
                if tax.lower() in col.lower():
                    dropped.append(col)
        dropped = list(set(dropped))
        df = df.drop(columns=dropped)

    # If provided, only include the specified samples.
    if sample_names:
        df = df.loc[sample_names]

    # Remove the metadata columns.
    dropped = []
    for column in df.columns:
        if 'Unassigned' in column:
            continue
        elif '__' in column:
            continue
        else:
            dropped.append(column)

    mf = df[dropped]
    mf = mf.assign(**{'sample-id': mf.index})
    df = df.drop(columns=dropped)




    # Convert counts to proportions.
    df = df.div(df.sum(axis=1), axis=0)

    # Sort the columns (i.e. species) by their mean abundance.
    df = df.loc[:, df.mean().sort_values(ascending=False).index]

    # If provided, collapse extra species to the Other column.
    if count is not 0:
        other = df.iloc[:, count-1:].sum(axis=1)
        df = df.iloc[:, :count-1]
        df['Other'] = other

    if sort_by_names:
        df = df.reindex(sorted(df.columns), axis=1)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    if show_legend and legend_short:
        def f(s):
            ranks = s.split(';')
            for rank in reversed(ranks):
                if rank != '__':
                    x = rank
                    break
            return x
        df.columns = [f(x) for x in df.columns]

    if colors:
        c = colors
    else:
        c = plt.cm.get_cmap('Accent').colors

    df2 = df * 100
    df2 = pd.melt(df2)

    if log_scale:
        ax.set_yscale('log')
        df2['value'].replace(0, 1, inplace=True)

    meanprops={'marker':'x',
               'markerfacecolor':'red', 
               'markeredgecolor':'red',
               'markersize':'10'}

    sns.boxplot(x='variable',
                y='value',
                data=df2,
                color='white',
                ax=ax,
                showmeans=True,
                meanprops=meanprops)

    sns.swarmplot(x='variable',
                  y='value',
                  data=df2,
                  ax=ax,
                  color='black',
                  size=size)

    ax.set_xlabel('')
    ax.set_ylabel('Relative abundance (%)')
    ax.set_ylim([1, 100])
    ax.tick_params(axis='x', labelrotation=90)



    # Control the x-axis labels.
    if hide_xlabels:
        ax.set_xticks([])
    elif label_columns:
        f = lambda row: ' : '.join(row.values.astype(str))
        new_labels = mf[label_columns].apply(f, axis=1)
        ax.set_xticklabels(new_labels)
    else:
        pass

    # Control the y-axis labels.
    if hide_ylabels:
        ax.set_ylabel('')
        ax.set_yticks([])

    # Control the legend.
    if show_legend:
        ax.legend(loc=legend_loc)

    # If provided, output the dataframe as a .csv file.
    if csv_file is not None:
        df.to_csv(csv_file)


    if xlabels is not None:
        xtexts = [x.get_text() for x in ax.get_xticklabels()]
        if len(xtexts) != len(xlabels):
            m = f"Expected {len(xtexts)} items, but found {len(xlabels)}"
            raise ValueError(m)
        ax.set_xticklabels(xlabels)






























def beta_2d_plot(ordination,
                 metadata,
                 hue=None,
                 size=None,
                 style=None,
                 s=80,
                 alpha=None,
                 ax=None,
                 figsize=None,
                 show_legend=False,
                 legend_loc='best'):
    """
    This method creates a 2D beta diversity plot.

    Parameters
    ----------
    ordination : str or qiime2.sdk.result.Artifact
        Artifact file or object from ordination.
    metadata : str or qiime2.metadata.metadata.Metadata
        Metadata file or object.
    hue : str, optional
        Grouping variable that will produce points with different colors.
    size : str, optional
        Grouping variable that will produce points with different sizes.
    style : str, optional
        Grouping variable that will produce points with different markers.
    s : int, default: 80
        Marker size.
    alpha : float, optional
        Proportional opacity of the points.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    show_legend : bool, default: False
        Show the legend.
    legend_loc : str, default: 'best'
        Legend location specified as in matplotlib.pyplot.legend.
    """
    t = TemporaryDirectory()

    if isinstance(ordination, qiime2.sdk.result.Artifact):
        fn = f'{t.name}/ordination.qza'
        ordination.save(fn)
        ordination = fn

    Artifact.load(ordination).export_data(t.name)

    df1 = pd.read_table(f'{t.name}/ordination.txt', header=None, index_col=0,
                        skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                        skipfooter=4, engine='python', usecols=[0, 1, 2])
    df1.columns = ['A1', 'A2']

    if isinstance(metadata, str):
        df2 = Metadata.load(metadata).to_dataframe()
    elif isinstance(metadata, qiime2.metadata.metadata.Metadata):
        df2 = metadata.to_dataframe()
    else:
        raise TypeError("Incorrect type of metadata detected")

    df3 = pd.concat([df1, df2], axis=1, join='inner')

    f = open(f'{t.name}/ordination.txt')
    explained_variances = [round(float(x) * 100, 2) for x
                               in f.readlines()[4].split('\t')]
    f.close()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)


    sns.scatterplot(data=df3, x='A1', y='A2', hue=hue, style=style, size=size, ax=ax, s=s, alpha=alpha)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(f'Axis 1 ({explained_variances[0]} %)')
    ax.set_ylabel(f'Axis 2 ({explained_variances[1]} %)')

    # Control the legend.
    if not hue and not size and not style:
        pass
    elif show_legend:
        ax.legend(loc=legend_loc)
    else:
        ax.get_legend().remove()















def beta_3d_plot(ordination,
                 metadata,
                 where,
                 azim=-60,
                 elev=30,
                 s=80, 
                 figsize=None,
                 ax=None,
                 show_legend=False,
                 legend_loc='best'):
    """
    This method creates a 3D beta diversity plot.

    Parameters
    ----------
    ordination : str
        Path to the artifact file from ordination (e.g. 
        bray_curtis_pcoa_results.qza).
    metadata : str
        Path to the sample-metadata.tsv file.
    where : str
        Column name of the sample metadata.
    azim : int, default: -60
        Elevation viewing angle.
    elev : int, default: 30
        Azimuthal viewing angle.
    s : int, default: 80
        Marker size.
    figsize : tuple of float, optional
        Width, height in inches.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    show_legend : bool, default: False
        Show the legend.
    legend_loc : str, default: 'best'
        Legend location specified as in matplotlib.pyplot.legend.
    """

    t = TemporaryDirectory()
    Artifact.load(ordination).export_data(t.name)

    df1 = pd.read_table(f'{t.name}/ordination.txt', header=None, index_col=0,
                        skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                        skipfooter=4, engine='python')
    df1 = df1.sort_index()

    df2 = Metadata.load(metadata).to_dataframe()
    df2 = df2.sort_index()

    f = open(f'{t.name}/ordination.txt')
    v = [round(float(x) * 100, 2) for x in f.readlines()[4].split('\t')]
    f.close()

    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1, projection='3d')

    ax.view_init(azim=azim, elev=elev)
    ax.set_xlabel(f'Axis 1 ({v[0]} %)')
    ax.set_ylabel(f'Axis 2 ({v[1]} %)')
    ax.set_zlabel(f'Axis 3 ({v[2]} %)')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    for c in sorted(df2[where].unique()):
        i = df2[where] == c
        ax.scatter(df1[i].iloc[:, 0], df1[i].iloc[:, 1],
                   df1[i].iloc[:, 2], label=c, s=s)

    # Control the legend.
    if show_legend:
        ax.legend(loc=legend_loc)























def distance_matrix_plot(distance_matrix,
                         bins=100,
                         pairs=None,
                         figsize=None, 
                         ax=None):
    """
    This method creates a histogram from a distance matrix.

    Parameters
    ----------
    distance_matrix : str or qiime2.sdk.result.Artifact
         Artifact file or object from distance matrix computation.
    bins : int, optional
        Number of bins to be displayed.
    pairs : list, optional
        List of sample pairs to be shown in red vertical lines.
    figsize : tuple of float, optional
        Width, height in inches.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    """
    t = TemporaryDirectory()

    if isinstance(distance_matrix, qiime2.sdk.result.Artifact):
        fn = f'{t.name}/distance-matrix.qza'
        distance_matrix.save(fn)
        distance_matrix = fn

    Artifact.load(distance_matrix).export_data(t.name)
    df = pd.read_table(f'{t.name}/distance-matrix.tsv', index_col=0)
    dist = sb.stats.distance.DistanceMatrix(df, ids=df.columns)
    cdist = dist.condensed_form()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax.hist(cdist, bins=bins)

    # https://stackoverflow.com/a/36867493/7481899
    def square_to_condensed(i, j, n):
        assert i != j, "no diagonal elements in condensed matrix"
        if i < j:
            i, j = j, i
        return n*j - j*(j+1)//2 + i - 1 - j

    if pairs:
        idx = []

        for pair in pairs:
            i = square_to_condensed(dist.index(pair[0]), dist.index(pair[1]), len(dist.ids))
            idx.append(cdist[i])

        for i in idx:
            ax.axvline(x=i, c='red')


































def denoising_stats_plot(stats,
                         metadata,
                         where,
                         ax=None,
                         figsize=None,
                         log_scale=False,
                         ylimits=None):
    """
    This method creates a grouped box plot using denoising statistics from 
    DADA2 (i.e. the 'qiime dada2 denoise-paired' command).

    Parameters
    ----------
    stats : str
        Path to the denoising-stats.qza file.
    metadata : str
        Path to the sample-metadata.tsv file.
    where : str
        Column name of the sample metadata.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    log_scale : bool, default: False
        Draw the y-axis in log scale.
    """
    t = TemporaryDirectory()
    Artifact.load(stats).export_data(t.name)
    df1 = pd.read_table(f'{t.name}/stats.tsv', skiprows=[1], index_col=0)
    df2 = Metadata.load(metadata).to_dataframe()
    df3 = pd.concat([df1, df2], axis=1, join='inner')
    dict = df3[where].value_counts().to_dict()
    for k, v in dict.items():
        dict[k] = f"{k} ({v})"
    df3[where].replace(dict, inplace=True)
    a = ['input', 'filtered', 'denoised', 'merged', 'non-chimeric', where]
    df4 = pd.melt(df3[a], id_vars=[where])
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    if log_scale:
        df4['value'].replace(0, 1, inplace=True)
        ax.set_yscale('log')

    sns.boxplot(x=where,
                y='value',
                data=df4,
                hue='variable',
                ax=ax)

    if ylimits:
        ax.set_ylim(ylimits)






















def paired_abundance_plot(taxa, x, y, hue, level=1, by=[],
                          exclude_samples={}, ax=None, figsize=None):
    """
    This method creates a line plot showing relative frequency of a specific 
    taxon for paired samples.

    Parameters
    ----------
    taxa : str
        Path to the visualization file from the 'qiime taxa barplot'.
    x : str
        The column to be used for the x-axis.
    y : str
        The column to be used for the y-axis (i.e. the taxon name).
    hue : str
        The column to be used for distinguishing the individual samples
    level : int
        Taxonomic level at which the features should be collapsed.
        within a pair.
    by : list of str
        Column name(s) to be used for sorting the samples. Using 'index' will 
        sort the samples by their name, in addition to other column name(s) 
        that may have been provided. If multiple items are provided, sorting 
        will occur by the order of the items.
    exclude_samples : dict of str to list of str
        Dictionary of column name(s) to list(s) of column value(s) to use to 
        exclude samples.
    ax : matplotlib.axes.Axes, optional
        Axes object to draw the plot onto, otherwise uses the current Axes.
    figsize : tuple of float, optional
        Width, height in inches.
    """
    t = TemporaryDirectory()
    Visualization.load(taxa).export_data(t.name)
    df = pd.read_csv(f'{t.name}/level-{level}.csv', index_col=0)

    # If provided, sort the samples for display in the x-axis.
    if by:
        df = df.sort_values(by=[hue] + by)

    # Remove the metadata columns.
    dropped = []
    for column in df.columns:
        if 'Unassigned' in column:
            continue
        elif '__' in column:
            continue
        else:
            dropped.append(column)
    mf = df[dropped]
    df = df.drop(columns=dropped)

    # Convert counts to proportions.
    df = df.div(df.sum(axis=1), axis=0)
    mf[y] = df[y]

    # If provided, exclude the specified samples.
    if exclude_samples:
        for xx in exclude_samples:
            for yy in exclude_samples[xx]:
                mf = mf[mf[xx] != yy]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    mf.rename(columns={y: 'Y'}, inplace=True)
    mf = mf[[x, 'Y', hue] + by]

    if by:
        temp = mf[by].apply(lambda row: ', '.join(row.values.astype(str)), axis=1)

        mf[x] = mf[x] + ' (' + temp + ')'

    sns.lineplot(data=mf, x=x, y='Y', hue=hue, marker='o', sort=False, ax=ax)
    ax.tick_params(axis='x', labelrotation=90)

    ax.set_xlabel('')
    ax.set_ylabel('Relative frequency')


