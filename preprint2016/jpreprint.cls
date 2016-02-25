% 平成27年度専攻科特別研究発表会予稿用クラスファイル
% 平成28年1月18日 作成
%                                          林 裕樹
\NeedsTeXFormat{pLaTeX2e}
\ProvidesClass{jpreprint}[2016/1/18 専攻科特別研究発表会予稿]
\ExecuteOptions{11pt,a4paper}
\ProcessOptions\relax

\LoadClass[]{jarticle}
\RequirePackage[dvips]{graphics}
\RequirePackage{times}
\RequirePackage{multicol}
\RequirePackage[a4paper]{geometry}

\def\m@rgintop{25truemm}
\def\m@rginbottom{25truemm}
\def\m@rginleft{25truemm}
\def\m@rginright{25truemm}

\geometry{
  top=\m@rgintop , %
  bottom=\m@rginbottom , %
  left=\m@rginleft , %
  right=\m@rginright, %
  asymmetric}

\newif\iflab
\newif\ifabstract
\newif\ifkeyword

\def\jtitle#1{\def\@jtitle{#1}}
\def\jauthor#1{\def\@jauthor{#1}}
\def\jlab#1{\def\@jlab{#1}\labtrue}
\def\jcourse#1{\def\@jcourse{#1}}
\def\course#1{\def\@course{#1}}
\def\abstract#1{\def\@abstract{#1}\abstracttrue}
\gdef\@keywords{\relax}
\def\keyword#1{\xdef\@keywords{\ifkeyword\@keywords, \fi#1}\keywordtrue}

\newenvironment{tablehere}
  {\def\@captype{table}}
  {}
\newenvironment{figurehere}
  {\def\@captype{figure}}
  {}

\def\maketitle{%
  \vbox {%
    \noindent
    \hbox to \textwidth{\vtop{\hsize=\textwidth\centering{\fontsize{18pt}{24pt}\selectfont\@jtitle}}}
    \vskip 8pt
    \noindent
    \hbox to \textwidth{\hss 釧路高専専攻科~~\@jcourse\iflab~~\@jlab 研究
      室\fi~~~~\@jauthor\hss}
    \ifabstract
    \vskip 8pt
    \noindent
    \hbox to \textwidth{\vtop{\hsize=\textwidth\centering{\fontsize{18pt}{24pt}\selectfont\@title}}}
    \vskip 8pt
    \noindent
    \hbox to \textwidth{\hss\@author\hss}
    \vskip 4pt
    \noindent
    \hbox to \textwidth{\vtop{\hsize=\textwidth\centering Advanced
        Course of \@course\par
      National Institute of Technology, Kushiro College}}
    \vskip 8pt
    \noindent
    \hbox to \textwidth{\hss{\bf Abstract}\hss}
    \dimen1=\textwidth\advance\dimen1 -30truemm
    \noindent
    \hbox to \textwidth{\hskip 15truemm\vtop{\hsize=\dimen1{\fontsize{10pt}{12pt}\selectfont\@abstract}}}
    \ifkeyword
    \vskip 8pt
    \noindent
    \hskip 15truemm\hbox to \dimen1{{\bf Keywords} \@keywords\hfil}
    \fi\fi}
}

\renewcommand{\thesection}{\fontsize{12pt}{12pt}\selectfont\arabic{section}.}
\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}.}
\renewcommand{\section}{\@startsection{section}{1}{\z@}%
   {.5\Cvs \@plus.5\Cvs \@minus.2\Cvs}%
   {.01\Cvs \@plus.3\Cvs}%
   {\reset@font\large\bfseries}}
\renewcommand{\subsection}{\@startsection{subsection}{2}{\z@}%
   {.5\Cvs \@plus.5\Cvs \@minus.2\Cvs}%
   {.01\Cvs \@plus.3\Cvs}%
   {\reset@font\normalsize\bfseries}}
\renewcommand{\subsubsection}{\@startsection{subsubsection}{3}{\z@}%
   {.5\Cvs \@plus.5\Cvs \@minus.2\Cvs}%
   {.01\Cvs \@plus.3\Cvs}%
   {\reset@font\normalsize\bfseries}}

\pagestyle{empty}

\kanjiskip=.1zw plus.75pt minus .5pt

\columnsep=\textwidth
\advance\columnsep -44zw        % 20chars x 2cols x 1.1(widened space)
\columnseprule=0pt
