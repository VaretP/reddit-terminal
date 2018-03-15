#!/usr/bin/env python

import os
import sys
import signal
import webbrowser
import curses as cs
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from pyfiglet import figlet_format


def signal_handler(signal, frame):
    sys.exit(0)


def look(entry, midcol, domain_r):
    domain = entry.div.find('span', {'class': 'domain'}).a['href']
    title_div = entry.div.p.a
    link = ''
    if domain not in ['/domain/i.redd.it/', domain_r]:
        link = title_div['href']
    comments = entry.div.ul.a['href']
    title = title_div.text
    time = entry.div.find('p', {'class': 'tagline '}).time.text
    score = midcol.find('div', {'class': 'score unvoted'}).text
    return(title, domain, link, comments, score, time)


def display(name, n, infos, text_window):
    text_window.refresh()
    text_window.clear()
    text_window.addstr(figlet_format(name, font='big'))
    text_window.addstr(str(n + 1) + ' : ' + infos[0] + '\nSubmitted '
                       + infos[5] + '\nScore = ' + infos[4])


def try_connection(url):
    try:
        return uReq(url)
    except HTTPError as e:
        time.sleep(2)
        return try_connection(url)


def navigate(sub_r, ranking, stdscr, window, text_window):
    name = sub_r
    domain_r = '/r/' + sub_r + '/'
    sub_r = 'https://www.reddit.com/r/' + sub_r + '/'
    if ranking == 'n':
        sub_r += 'new/'
    elif ranking == 't':
        sub_r += 'top/'
    uClient = try_connection(sub_r)
    html = uClient.read()
    uClient.close()
    page_soup = soup(html, 'html.parser')
    entries = page_soup.findAll('div', {'class': 'entry unvoted'})
    midcols = page_soup.findAll('div', {'class': 'midcol unvoted'})
    n_max = len(entries) - 1
    n = -1
    text_window.refresh()
    text_window.clear()
    text_window.addstr(figlet_format(name, font='big'))
    text_window.addstr('Welcome to the ' + name + ' subreddit !')
    stdscr.addstr(cs.LINES - 1, 0, ' (N)New (H)Hot (T)Top (Q)Quit        '
                  + '              ')
    if ranking == 'n':
        stdscr.chgat(cs.LINES - 1, 1, 3, cs.A_BOLD | cs.color_pair(3))
    elif ranking == 'h':
        stdscr.chgat(cs.LINES - 1, 8, 3, cs.A_BOLD | cs.color_pair(3))
    elif ranking == 't':
        stdscr.chgat(cs.LINES - 1, 15, 3, cs.A_BOLD | cs.color_pair(3))
    stdscr.chgat(cs.LINES - 1, 22, 3, cs.A_BOLD | cs.color_pair(1))
    stdscr.noutrefresh()
    window.noutrefresh()
    text_window.noutrefresh()
    cs.doupdate()
    while 1:
        char = window.getch()
        if char == 66:
            n += 1
            if n > n_max:
                n = 0
            display(name, n, look(entries[n], midcols[n], domain_r),
                    text_window)
        elif char == 65:
            n -= 1
            if n < 0:
                n = n_max
            display(name, n, look(entries[n], midcols[n], domain_r),
                    text_window)
        elif char == 67 or char == 68:
            (title, domain, link, comments, score, time) \
                    = look(entries[n], midcols[n], domain_r)
            if char == 68 or link == '':
                webbrowser.open(comments)
            else:
                webbrowser.open(link)
        elif char == ord('n') or char == ord('N'):
            navigate(name, 'n', stdscr, window, text_window)
            break
        elif char == ord('t') or char == ord('T'):
            navigate(name, 't', stdscr, window, text_window)
            break
        elif char == ord('h') or char == ord('H'):
            navigate(name, 'h', stdscr, window, text_window)
            break
        elif char == ord('q') or char == ord('Q'):
            break
        stdscr.noutrefresh()
        window.noutrefresh()
        text_window.noutrefresh()
        cs.doupdate()


def main():
    stdscr = cs.initscr()
    cs.noecho()
    cs.cbreak()
    cs.curs_set(0)
    if cs.has_colors():
        cs.start_color()
    cs.init_pair(1, cs.COLOR_RED, cs.COLOR_BLACK)
    cs.init_pair(2, cs.COLOR_GREEN, cs.COLOR_BLACK)
    cs.init_pair(3, cs.COLOR_BLUE, cs.COLOR_BLACK)
    stdscr.addstr(" Reddit Terminal", cs.A_REVERSE)
    stdscr.chgat(-1, cs.A_REVERSE)
    stdscr.addstr(cs.LINES - 1, 0, ' Press (I) to enter a subreddit, '
                  + 'Press (Q) to leave')
    stdscr.chgat(cs.LINES - 1, 7, 3, cs.A_BOLD | cs.color_pair(2))
    stdscr.chgat(cs.LINES - 1, 39, 3, cs.A_BOLD | cs.color_pair(1))
    window = cs.newwin(cs.LINES - 2, cs.COLS, 1, 0)
    text_window = window.subwin(cs.LINES - 6, cs.COLS - 4, 3, 3)
    text_window.addstr(figlet_format('Reddit', font='big'))
    window.box()
    stdscr.noutrefresh()
    window.noutrefresh()
    cs.doupdate()
    text_window.scrollok(1)
    while 1:
        char = window.getch()
        if char == ord('i') or char == ord('I'):
            text_window.clear()
            cs.curs_set(1)
            cs.echo()
            text_window.addstr(figlet_format('Reddit', font='big'))
            text_window.addstr('Enter a subreddit name :')
            s = text_window.getstr(8, 25, 30)
            text_window.refresh()
            text_window.clear()
            cs.curs_set(0)
            cs.noecho()
            navigate(s.decode('utf-8'), 'n',  stdscr, window, text_window)
            stdscr.addstr(cs.LINES - 1, 0, ' Press (I) to enter a subreddit, '
                          + 'Press (Q) to leave')
            stdscr.chgat(cs.LINES - 1, 7, 3, cs.A_BOLD | cs.color_pair(2))
            stdscr.chgat(cs.LINES - 1, 39, 3, cs.A_BOLD | cs.color_pair(1))
            text_window.refresh()
            text_window.clear()
        if char == ord('q') or char == ord('Q'):
            break
        if char == 65 or char == 66:
            text_window.refresh()
            text_window.clear()
        text_window.addstr(figlet_format('Reddit', font='big'))
        stdscr.noutrefresh()
        window.noutrefresh()
        text_window.noutrefresh()
        cs.doupdate()
    cs.nocbreak()
    cs.echo()
    cs.curs_set(1)
    cs.endwin()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
