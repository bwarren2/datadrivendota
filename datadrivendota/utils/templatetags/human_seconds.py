# Import template library
from django import template
from datetime import datetime

# Set register
register = template.Library()


# Register filter
@register.filter(name='human_seconds')
def human_seconds(value, arg=''):
    """ Turn seconds into a pretty string. """
    # Place seconds in to integer
    secs = int(value)

    # If seconds are greater than 0
    if secs > 0:

        # Import math library
        import math

        # Place durations of given units in to variables
        day_seconds = 86400
        hour_seconds = 3600
        minute_seconds = 60

        # If short string is enabled
        if arg != 'long':

            # Set short names
            day_unit = ' day'
            hour_unit = ' hr'
            minute_unit = ' min'
            second_unit = ' sec'

            # Set short duration unit splitters
            last_duration_splitter = ' '
            next_duration_splitter = last_duration_splitter

        # If short string is not provided or any other value
        else:

            # Set long names
            day_unit = ' day'
            hour_unit = ' hour'
            minute_unit = ' minute'
            second_unit = ' second'

            # Set long duration unit splitters
            last_duration_splitter = ' and '
            next_duration_splitter = ', '

        # Create string to hold outout
        duration_string = ''

        # Calculate number of days from seconds
        days = int(math.floor(secs / int(day_seconds)))

        # Subtract days from seconds
        secs = secs - (days * int(day_seconds))

        # Calculate number of hours from seconds (minus number of days)
        hours = int(math.floor(secs / int(hour_seconds)))

        # Subtract hours from seconds
        secs = secs - (hours * int(hour_seconds))

        # Calculate number of minutes from seconds (minus number of days and hours)
        minutes = int(math.floor(secs / int(minute_seconds)))

        # Subtract days from seconds
        secs = secs - (minutes * int(minute_seconds))

        # Calculate number of seconds (minus days, hours and minutes)
        seconds = secs

        # If number of days is greater than 0
        if days > 0:

            # Add multiple days to duration string
            duration_string += ' ' + str(days) + day_unit + (days > 1 and 's' or '')

        # Determine if next string is to be shown
        if hours > 0:

            # If there are no more units after this
            if minutes <= 0 and seconds <= 0:

                # Set hour splitter to last
                hour_splitter = last_duration_splitter

            # If there are unit after this
            else:

                # Set hour splitter to next
                hour_splitter = (len(duration_string) > 0 and next_duration_splitter or '')

        # If number of hours is greater than 0
        if hours > 0:

            # Add multiple days to duration string
            duration_string += hour_splitter + ' ' + str(hours) + hour_unit + (hours > 1 and 's' or '')

        # Determine if next string is to be shown
        if minutes > 0:

            # If there are no more units after this
            if seconds <= 0:

                # Set minute splitter to last
                minute_splitter = last_duration_splitter

            # If there are unit after this
            else:

                # Set minute splitter to next
                minute_splitter = (len(duration_string) > 0 and next_duration_splitter or '')

        # If number of minutes is greater than 0
        if minutes > 0:

            # Add multiple days to duration string
            duration_string += minute_splitter + ' ' + str(minutes) + minute_unit + (minutes > 1 and 's' or '')

        # Determine if next string is last
        if seconds > 0:

            # Set second splitter
            second_splitter = (len(duration_string) > 0 and last_duration_splitter or '')

        # If number of seconds is greater than 0
        if seconds > 0:

            # Add multiple days to duration string
            duration_string += second_splitter + ' ' + str(seconds) + second_unit + (seconds > 1 and 's' or '')

        # Return duration string
        return duration_string.strip()

    # If seconds are not greater than 0
    else:

        # Provide 'No duration' message
        return 'No duration'


@register.filter(name='seconds_to_date')
def seconds_to_date(value, arg=''):
    """ Turn seconds into a pretty string. """
    # Place seconds in to integer
    return datetime.fromtimestamp(value)
