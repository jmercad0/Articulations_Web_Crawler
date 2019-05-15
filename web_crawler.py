# ----------------------------------------------------------------------
# Name:         CS 122: HW #9 (SJSU Course Articulation Web Crawler)
# Author:       Jordan Mercado
# Purpose:      To implement a Web Crawler Application with urllib &
#               BeautifulSoup. Takes information from
#               'http://info.sjsu.edu/web-dbgen/artic/all-course-to-cour
#               se.html' and writes output to 'articulations.txt'
#
# Date:         4/16/2019
# ----------------------------------------------------------------------
import bs4
import urllib.request
import urllib.parse
import urllib.robotparser
import urllib.error



def extract_from_all_pages(pages, equiv):
    """
    Applies extract_information to all pages from list of links

    :param pages:  (list) list of url links to be crawled
    :param equiv:  (dict) information on articulation translations
    :return equiv:  (list) modified information on articulations
    """
    print('Extracting information from all URL links...')
    courses = ('CS 046A', 'CS 046B', 'CS 047', 'CS 049C', 'CS 049J')

    # Extract information from all pages in list of links
    for links in pages:
        equiv = extract_information(links, equiv, courses)
    return equiv

def write_to_file(equiv):
    """
    Formats and writes extracted information to 'articulations.txt'

    :param equiv:  (dict) articulation information to format as W output
    """
    print('Writing to file...')
    # Open/create file to write/overwrite to
    write_file = open("articulations.txt", "w")
    # For each CS course observed, write respective articulation to file
    for course in equiv:
        for articulation in equiv[course]:
            write_file.write(course + ': ' + articulation + '\n')

def extract_information(url_link, equiv_dict, courses):
    """
    Formats and writes extracted information to 'articulations.txt'

    :param url_link:  (str) url of page to extract information from
    :param equiv_dict:  (dict) articulation information to be updated
    :param courses:  (set) SJSU CS courses to check articulations for
    :return:  (dict) articulation information updated with page info
    """
    # Request access to url page & open for reading
    req = urllib.request.Request(url = url_link)
    with urllib.request.urlopen(req) as url_file:
        url = url_file.read()
        # Create soup object to parse html content of page
        soup = bs4.BeautifulSoup(url, "html.parser")
        # Find main table holding school & course information
        equiv_table_rows = (soup.find('div', id = 'bg').find('div',
        id = 'content').find('div', {'class': 'content_wrapper'})
            .find_all('table')[1].find_all('tr'))
        # Find name of school
        school = equiv_table_rows[0].find_all('td')[2].get_text()

        # For each row in main information table, find course info
        # and check if matches valid CS course articulation
        for tr in equiv_table_rows:
            entries = tr.find_all('td')
            course = entries[0].get_text()[:7].strip(' ')
            # If CS course has valid equivalent articulation
            if course in courses and entries[2].get_text() \
                    != "No Current Equivalent":
                # Get course articulation info & format data
                text = entries[2].get_text().replace(u'\xa0', '').replace(
                    'AND', ' AND ').replace('OR', ' OR ')
                # Cover corner case collision for 'OR' replacement
                if 'HON OR S' in text:
                    text = text.replace('HON OR S', 'HONORS')
                # Append to course entry of articulations
                equiv_dict[course].append(text + ' at '+ school)

        return equiv_dict



def extract_links():
    """
    Reads base url and returns list of links to be parsed

    :return (list) list of all relative links to articulation lists
    """
    print('Extracting links from main URL page...')
    # request URL file to extract links from
    req = urllib.request.Request(
        url = 'http://info.sjsu.edu/web-dbgen/artic/all-course-to-course.html',
        data = b'This data is passed to stdin of the CGI')

    with urllib.request.urlopen(req) as url_file:
        # read file and create beautiful soup object to parse html
        url = url_file.read()
        soup = bs4.BeautifulSoup(url, "html.parser")
        # extract relative urls and attach to base url to create links
        rel_links = [anchor.find('td').find('a').get('href', None) for anchor
                    in soup.find_all('table')[2].find_all('tr')]
        base_url = "http://info.sjsu.edu/"

        # return list of abs_urls created from joining base & rel URLS
        return [urllib.parse.urljoin(base_url, link) for link in rel_links]


def ok_to_crawl(url):
    """
    Checks if page is polite to crawl

    :param url: (str) base URL to check if polite to crawl
    :return:  (boolean) return true if polite to crawl, else false
    """
    parsed_url = urllib.parse.urlparse(url)
    # Build the corresponding robots.txt url name
    robot = urllib.parse.urljoin(f'{parsed_url.scheme}://{parsed_url.netloc}',
                                 '/robots.txt')
    user_agent = urllib.request.URLopener.version  # user -agent
    # Create robot parser object to check protocol of crawling url file
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robot)
    try:
        rp.read()
    except urllib.error.URLError as url_err:
        print(parsed_url, robot, url_err)
        return False
    else:
        return rp.can_fetch(user_agent, parsed_url)


def main():
    """
    Main function to call helper methods to crawl web page and
    write output to file.
    """
    # Initialize dictionary to be used to store articulation info
    courses = ('CS 046A', 'CS 046B', 'CS 047', 'CS 049C', 'CS 049J')
    equiv = {classes: [] for classes in courses}
    # Check if page is polite to crawl
    polite = ok_to_crawl(
        'http://info.sjsu.edu/web-dbgen/artic/all-course-to-course.html')
    # If polite, continue to extract information, write output to file
    if polite:
        print('Polite to crawl. Begin crawling. This may take a few moments.')
        pages = extract_links()
        equiv = extract_from_all_pages(pages, equiv)
        write_to_file(equiv)
        print('Web crawl complete. Check articulations.txt for output.')
    # End program if not polite or network error
    else:
        print('Error: Not polite to crawl or problem connecting to network.')
        return None


if __name__ == '__main__':
    main()
