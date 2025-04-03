def generate_latex_report(dimx, dimy, dimz, mass, slope, wind_force, friction_coeff, lashings_data, transverse_result, longitudinal_result):
    latex_content = r"""\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{float}
\usepackage{siunitx}

\geometry{a4paper, margin=1in}
\title{Lashing Calculation Report}
\author{Lashing Calculator}
\date{\today}

\begin{document}
\maketitle

\section{Input Parameters}

\subsection{Load Specifications}
\begin{table}[H]
\centering
\begin{tabular}{ll}
\toprule
Parameter & Value \\
\midrule
Length (X) & \SI{%s}{m} \\
Width (Y) & \SI{%s}{m} \\
Height (Z) & \SI{%s}{m} \\
Mass & \SI{%s}{tonnes} \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Environmental Conditions}
\begin{table}[H]
\centering
\begin{tabular}{ll}
\toprule
Parameter & Value \\
\midrule
Slope & \SI{%s}{\degree} \\
Wind Force & Beaufort %s \\
Friction Coefficient & %s \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Lashing Configurations}
\begin{table}[H]
\centering
\begin{tabular}{cccccc}
\toprule
Lashing & $\alpha$ & $\beta$ & Breaking Strength & Side \\
\midrule
""" % (
        dimx, dimy, dimz, mass,
        slope, wind_force, friction_coeff
    )

    # Add lashing configurations
    for i, lashing_data in enumerate(lashings_data, 1):
        latex_content += r"%d & \SI{%s}{\degree} & \SI{%s}{\degree} & \SI{%s}{Tonnes} & %s \\" % (
            i, lashing_data['alpha'], lashing_data['beta'], 
            lashing_data['breaking_strength'], lashing_data['side']
        )
        latex_content += "\n"

    latex_content += r"""\bottomrule
\end{tabular}
\end{table}

\section{Calculation Results}

\subsection{Transverse Sliding Analysis}
\begin{verbatim}
%s
\end{verbatim}

\subsection{Longitudinal Sliding Analysis}
\begin{verbatim}
%s
\end{verbatim}

\section{Lashing Configuration Diagram}
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{pics/lashingPic.png}
\caption{Lashing Configuration}
\end{figure}

\end{document}""" % (
        "\n".join(transverse_result),
        "\n".join(longitudinal_result)
    )

    # Write to file
    with open("lashing_report.tex", "w") as f:
        f.write(latex_content) 