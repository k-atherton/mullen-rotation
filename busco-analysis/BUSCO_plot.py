#!/usr/bin/env python
"""
.. module:: BUSCO_plot
   :synopsis: This module produces a graphic summary for BUSCO runs based on short summary files
.. moduleauthor:: Mathieu Seppey <mathieu.seppey@unige.ch>
.. versionadded:: 2.0
.. versionchanged:: 2.0

 This module produces a graphic summary for BUSCO runs based on short summary files

(``python BUSCO_plot.py -h`` and user guide for details on how to do it)

Place the short summary files of all BUSCO runs you would like to see on the figure in the ``plot_data`` folder,
located at the BUSCO root. Keep the file named as follow: ``short_summary_label.txt``, label being used in the plot

This tool produces the R code of the figure and uses ggplot2. If your system seems able to run R, this script
automatically runs it.

You can find both the resulting R script for customisation and the figure if produced in the ``plot_data`` folder.

"""

import os
import sys
import time
import traceback
import argparse
import subprocess
from argparse import RawTextHelpFormatter
import logging
try:
    import BUSCO
except ImportError:
    print('ERROR:%s\tImpossible to locate the BUSCO main file (BUSCO.py) in the current folder' % __file__)
    raise SystemExit

#: working directory
_plot_dir = ''
#: r file name
_r_file = 'busco_figure.R'

# to avoid running R
_no_r = False

#: Get an instance of _logger for keeping track of events
logging.setLoggerClass(BUSCO.BUSCOLogger)
_logger = logging.getLogger(__file__.split("/")[-1])

RCODE = '######################################\n'\
        '#\n'\
        '# BUSCO summary figure\n'\
        '# @author Mathieu Seppey <mathieu.seppey@unige.ch>\n'\
        '# @version 2.0\n'\
        '# @since BUSCO 2.0\n'\
        '# \n'\
        '# Copyright (C) 2016 E. Zdobnov lab\n'\
        '# \n'\
        '# BUSCO is free software: you can redistribute it and/or modify\n'\
        '# it under the terms of the GNU General Public License as published by\n'\
        '# the Free Software Foundation, either version 3 of the License, or\n'\
        '# (at your option) any later version. See <http://www.gnu.org/licenses/>\n'\
        '#  \n'\
        '# BUSCO is distributed in the hope that it will be useful,\n'\
        '# but WITHOUT ANY WARRANTY; without even the implied warranty of\n'\
        '# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'\
        '# GNU General Public License for more details.\n'\
        '#\n'\
        '######################################\n'\
        '\n'\
        '# Load the required libraries\n'\
        'library(ggplot2)\n'\
        'library("grid")\n'\
        '\n'\
        '# !!! CONFIGURE YOUR PLOT HERE !!! \n'\
        '# Output\n'\
        'my_output <- paste(%s1,"busco_figure.png",sep="/") \n' \
        'my_width <- 20\n' \
        'my_height <- 30\n'\
        'my_unit <- "cm"\n'\
        '\n'\
        '# Colors\n'\
        'my_colors <- c("#56B4E9", "#3492C7", "#F0E442", "#F04442")\n'\
        '# Bar height ratio\n'\
        'my_bar_height <- 0.75\n'\
        '\n'\
        '# Legend\n'\
        'my_title <- "BUSCO Assessment Results"\n'\
        '\n'\
        '# Font\n'\
        'my_family <- "sans"\n'\
        'my_size_ratio <- 1\n'\
        '\n'\
        '# !!! SEE YOUR DATA HERE !!! \n'\
        '# Your data as generated by python, remove or add more\n'\
        'my_species <- c%s2\n'\
        'my_species <- factor(my_species)\n'\
        'my_species <- factor(my_species,levels(my_species)[c(length(levels(my_species)):1)]) ' \
        '# reorder your species here just by changing the values in the vector :\n'\
        'my_percentage <- c%s3\n'\
        'my_values <- c%s4\n'\
        '\n'\
        '######################################\n'\
        '######################################\n'\
        '######################################\n'\
        '# Code to produce the graph\n' \
        'labsize = 1\n' \
        'if (length(levels(my_species)) > 10){\n'\
        ' labsize = 0.66\n'\
        '}\n'\
        'print("Plotting the figure ...")\n'\
        'category <- c(rep(c("S","D","F","M"),c%s5))\n'\
        'category <-factor(category)\n'\
        'category = factor(category,levels(category)[c(4,1,2,3)])\n'\
        'df = data.frame(my_species,my_percentage,my_values,category)\n'\
        '\n'\
        'figure <- ggplot() + \n'\
        '  \n'\
        '  geom_bar(aes(y = my_percentage, x = my_species, fill = category), data = df, stat="identity", ' \
        'width=my_bar_height) + \n'\
        '  coord_flip() + \n' \
        '  theme_gray(base_size = 8) + \n' \
        '  scale_y_continuous(labels = c("0","20","40","60","80","100"), breaks = c(0,20,40,60,80,100)) + \n'\
        '  scale_fill_manual(values = my_colors,labels =c(" Complete (C) and single-copy (S)  ",\n'\
        '                                                 " Complete (C) and duplicated (D)",\n'\
        '                                                 " Fragmented (F)  ",\n'\
        '                                                 " Missing (M)")) +   \n'\
        '  ggtitle(my_title) + \n'\
        '  xlab("") + \n'\
        '  ylab("\\n%BUSCOs") + \n'\
        '\n'\
        '  theme(plot.title = element_text(family=my_family, colour = "black", size = rel(2.2)*my_size_ratio, face = ' \
        '"bold")) + \n'\
        '  theme(legend.position="top",legend.title = element_blank()) + \n'\
        '  theme(legend.text = element_text(family=my_family, size = rel(1.2)*my_size_ratio)) + \n'\
        '  theme(panel.background = element_rect(color="#FFFFFF", fill="white")) + \n'\
        '  theme(panel.grid.minor = element_blank()) + \n'\
        '  theme(panel.grid.major = element_blank()) +\n'\
        '  theme(axis.text.y = element_text(family=my_family, colour = "black", size = rel(1.66)*my_size_ratio)) + \n'\
        '  theme(axis.text.x = element_text(family=my_family, colour = "black", size = rel(1.66)*my_size_ratio)) + \n'\
        '  theme(axis.line = element_line(size=1*my_size_ratio, colour = "black")) + \n'\
        '  theme(axis.ticks.length = unit(.85, "cm")) + \n'\
        '  theme(axis.ticks.y = element_line(colour="white", size = 0)) + \n'\
        '  theme(axis.ticks.x = element_line(colour="#222222")) + \n'\
        '  theme(axis.ticks.length = unit(0.4, "cm")) + \n'\
        '  theme(axis.title.x = element_text(family=my_family, size=rel(1.2)*my_size_ratio)) + \n'\
        '  \n'\
        '  guides(fill = guide_legend(override.aes = list(colour = NULL))) +\n'\
        '  guides(fill=guide_legend(nrow=2,byrow=TRUE))\n'\
        '  \n'\
        '  for(i in rev(c(1:length(levels(my_species))))){\n'\
        '    detailed_values <- my_values[my_species==my_species[my_species==levels(my_species)[i]]]\n'\
        '    total_buscos <- sum(detailed_values)\n'\
        '    figure <- figure + \n' \
        '    annotate("text", label=paste("C:", detailed_values[1] + detailed_values[2], " [S:", detailed_values[1], ' \
        '", D:", detailed_values[2], "], F:", detailed_values[3], ", M:", detailed_values[4], ", n:", total_buscos, ' \
        'sep=""), \n' \
        '             y=3, x = i, size = labsize*4*my_size_ratio, colour = "black", hjust=0, family=my_family)\n'\
        '  }\n'\
        '  \n'\
        'ggsave(figure, file=my_output, width = my_width, height = my_height, unit = my_unit)\n'\
        'print("Done")\n'


def _check_wd():
    """
    This function checks that the working directory exists with write permission
    :raises SystemExit: if the folder is absent or the user has no write permission
    """
    if not os.path.exists(_plot_dir):
        _logger.warning('Impossible to read %s' % _plot_dir)
        raise SystemExit
    if not os.access(_plot_dir, os.W_OK):
        _logger.warning('Impossible to write into %s' % _plot_dir)
        raise SystemExit


def _write_r_code(data):
    """
    This function write the R code in its own file
    :param data: the data loaded from the run folders used to generate the R file
    :type data: dict
    """
    r_file = open('%s%s' % (_plot_dir, _r_file), 'w')
    r_file.write(RCODE
                 .replace('%s1', '"%s"' % _plot_dir)
                 .replace('%s2', str(tuple(data['species'])))
                 .replace('%s3', str(tuple(data['percentages'])))
                 .replace('%s4', str(tuple(data['values'])))
                 .replace('%s5', '(1)'))


def _run_r_code():
    """
    This function runs the R code after it was generated
    It first checks that ggplot2 related libraries are present
    """
    # first try to load the two required package and warn the user if an error occur
    # package ggplot2
    need_to_exit = False
    ggplot2 = subprocess.Popen(['R', '-e', 'library(ggplot2)', '--quiet'],
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ggplot2_out = ggplot2.stderr.readlines() + ggplot2.stdout.readlines()
    if 'Error' in str(ggplot2_out):
        _logger.warning('Impossible to run R. The package ggplot2 does not seem to be installed. '
                        'Please check your R installation. See also the --no_r option to avoid this message')
        need_to_exit = True

    # package grid
    grid = subprocess.Popen(['R', '-e', 'library(grid)', '--quiet'],
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    grid_out = grid.stderr.readlines() + grid.stdout.readlines()
    if 'Error' in str(grid_out):
        _logger.warning('Impossible to run R. The package grid does not seem to be installed. '
                        'Please check your R installation. See also the --no_r option to avoid this message')
        need_to_exit = True

    if need_to_exit:
        return None  # do not run the code, but no need to stop the execution

    # run R
    BUSCO.Analysis.p_open(['Rscript', '%s%s' % (_plot_dir, _r_file)], _r_file)


def _set_args():
    """
    This function sets the parameters provided by the user
    """
    parser = argparse.ArgumentParser(description='BUSCO %s plot generation tool.\n'
                                                 'Place all BUSCO short summary files in a single folder. '
                                                 'It will be '
                                                 'your working directory, in which the generated plot files'
                                                 ' will be written'
                                                 '\nSee also the user guide'
                                                 ' for additional information' % BUSCO.VERSION,
                                     usage='python BUSCO_plot.py -wd [WORKING_DIRECTORY] [OTHER OPTIONS]',
                                     formatter_class=RawTextHelpFormatter, add_help=False)

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '-wd', '--working_directory', metavar='PATH', required=True, dest='working_directory',
        help='Define the location of your working directory')
    optional.add_argument(
        '--no_r', help='To avoid to run R. It will just create the R script file in the working directory',
        action="store_true", dest='no_r')
    optional.add_argument(
        '-q', '--quiet', help='Disable the info logs, displays only errors', action="store_true", dest='quiet')
    optional.add_argument('-v', '--version', action='version', help="Show this version and exit",
                          version='BUSCO %s' % BUSCO.VERSION)
    optional.add_argument('-h', '--help', action="help", help="Show this help message and exit")
    args = vars(parser.parse_args())
    if args["quiet"]:
        _logger.setLevel(logging.ERROR)
    if args["no_r"]:
        global _no_r
        _no_r = True
    global _plot_dir
    _plot_dir = args["working_directory"]
    if _plot_dir[-1] != '/':
        _plot_dir += '/'


def _load_data():
    """

    :return:
    """
    data = {'species': [], 'values': [], 'percentages': []}
    for f in os.listdir(_plot_dir):
        if f.startswith('short_summary_'):
            try:
                content = open('%s/%s' % (_plot_dir, f))
                comp = 0
                dupl = 0
                frag = 0
                miss = 0
                for line in content:
                    if 'Complete and single-copy BUSCOs' in line:
                        comp = int(line.split('\t')[1])
                    elif 'Complete and duplicated BUSCOs' in line:
                        dupl = int(line.split('\t')[1])
                    elif 'Fragmented BUSCOs' in line:
                        frag = int(line.split('\t')[1])
                    elif 'Missing BUSCOs' in line:
                        miss = int(line.split('\t')[1])
                data['species'] += [f[14:].split('.txt')[0]]*4
                data['values'] += [comp, dupl, frag, miss]
                total = comp + dupl + frag + miss
                comp_pc = round(comp/float(total)*100, 1)
                dupl_pc = round(dupl/float(total)*100, 1)
                frag_pc = round(frag/float(total)*100, 1)
                miss_pc = round(100 - comp_pc - dupl_pc - frag_pc, 1)
                data['percentages'] += [comp_pc, dupl_pc, frag_pc, miss_pc]
                _logger.info('Loaded %s sucessfully' % f)
            except IOError:
                _logger.warning('Impossible to use the file %s' % f)
    if len(data['species']) == 0:
        _logger.warning('No short summary found in %s' % _plot_dir)
        raise SystemExit
    return data


def main():
    """
    This function produces a figure with all BUSCO runs present in the current folder
    """

    _set_args()  # Fetch the params provided by the user
    start_time = time.time()
    _logger.add_blank_line()

    try:

        _logger.info('****************** Start plot generation at %s ******************'
                     % (time.strftime("%m/%d/%Y %H:%M:%S")))

        # check working directory
        _check_wd()
        # load data
        _logger.info('Load data ...')
        data = _load_data()

        # write R code
        _logger.info('Generate the R code ...')
        _write_r_code(data)

        # run R code
        if not _no_r:
            if BUSCO.Analysis.cmd_exists('Rscript'):
                _logger.info('Run the R code ...')
                _run_r_code()
            else:
                _logger.warning('Impossible to run R. Rscript command is not accessible. '
                                'Please check your R installation or use --no_r to avoid this message')
        else:
            _logger.info('You chose not to run R')

        _logger.add_blank_line()
        if not _logger.has_warning():
            _logger.info('Plot generation done. Total running time: %s seconds' % str(time.time() - start_time))
        else:
            _logger.info('Plot generation done with WARNING(s). Total running time: %s seconds'
                         % str(time.time() - start_time))
        _logger.info('Results written in %s\n' % _plot_dir)

    except SystemExit:
        _logger.add_blank_line()
        _logger.error('Plot generation failed !')
        _logger.info(
            'Check the logs, read the user guide, if you still need technical support, then please contact %s\n'
            % BUSCO.CONTACT)
        raise SystemExit

    except KeyboardInterrupt:
        _logger.add_blank_line()
        _logger.error('A signal was sent to kill the process')
        _logger.error('Plot generation failed !')
        _logger.info(
            'Check the logs, read the user guide, if you still need technical support, then please contact %s\n'
            % BUSCO.CONTACT)
        raise SystemExit

    except BaseException:
        _logger.add_blank_line()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        _logger.critical('Unhandled exception occurred: %s' % repr(traceback.format_exception(exc_type, exc_value,
                                                                                              exc_traceback)))
        _logger.error('Plot generation failed !\n')
        _logger.info(
            'Check the logs, read the user guide, if you still need technical support, then please contact %s\n'
            % BUSCO.CONTACT)
        raise SystemExit


# Entry point
if __name__ == "__main__":
    main()