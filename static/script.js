// script.js
$(document).ready(function() {
    $('#date_time').on('change', function() {
        const dateTime = new Date($(this).val());
        
        // Extract hour of the day
        const hour = dateTime.getHours();
        $('#hour_of_day').val(hour);

        // Extract day of the week
        const dayOfWeek = dateTime.toLocaleString('en-US', { weekday: 'long' });
        $('#day_of_week').val(dayOfWeek);

        // Determine if it's a weekend
        const isWeekend = (dayOfWeek === 'Saturday' || dayOfWeek === 'Sunday') ? 1 : 0;
        $('#is_weekend').val(isWeekend);
    });
});
