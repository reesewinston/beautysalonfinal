# file for all database query functions
"""database query functions for the beauty salon management system"""

# import connection function
from connection import createConnection


# run SELECT queries (get data)
def run_select(query, params=None):
    conn = createConnection()  # connect to database
    if not conn:
        return []

    try:
        cursor = conn.cursor()  # create cursor
        cursor.execute(query, params or ())  # run query
        rows = cursor.fetchall()  # get results
        return rows
    except Exception as e:
        print(f'select error: {e}')
        return []
    finally:
        try:
            cursor.close()  # close cursor
            conn.close()  # close connection
        except Exception:
            pass


# run INSERT, UPDATE, DELETE queries
def run_action(query, params=None):
    conn = createConnection()
    if not conn:
        return False, None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()  # save changes
        return True, cursor.lastrowid  # return success + id
    except Exception as e:
        print(f'action error: {e}')
        conn.rollback()  # undo if error
        return False, None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# get all service categories
def get_categories():
    rows = run_select('select distinct category from services order by category')
    return [row[0] for row in rows]


# get stylists based on category
def get_stylists_for_category(category):
    query = """
    select distinct concat(st.first_name, ' ', st.last_name) as name
    from stylists st
    join stylist_services ss on st.stylist_id = ss.stylist_id
    join services sv on ss.service_id = sv.service_id
    where sv.category = %s
    order by name
    """
    rows = run_select(query, (category,))
    return [row[0] for row in rows]


# get stylist ratings and most booked service
def get_stylist_stats(category):
    query = """
    select 
        concat(st.first_name, ' ', st.last_name) as stylist,
        coalesce(round(avg(r.rating), 1), 0) as avg_rating,
        coalesce(
            (
                select sv2.service_name
                from appointments a2
                join services sv2 on a2.service_id = sv2.service_id
                where a2.stylist_id = st.stylist_id
                group by sv2.service_id, sv2.service_name
                order by count(*) desc
                limit 1
            ),
            'none yet'
        ) as most_booked_service
    from stylists st
    left join appointments a on st.stylist_id = a.stylist_id
    left join reviews r on a.appointment_id = r.appointment_id
    where st.specialty = %s
    group by st.stylist_id, st.first_name, st.last_name
    order by st.first_name, st.last_name
    """
    return run_select(query, (category,))


# get services for a stylist
def get_services_for_stylist(category, first_name, last_name):
    query = """
    select sv.service_name
    from services sv
    join stylist_services ss on sv.service_id = ss.service_id
    join stylists st on ss.stylist_id = st.stylist_id
    where sv.category = %s and st.first_name = %s and st.last_name = %s
    order by sv.service_name
    """
    rows = run_select(query, (category, first_name, last_name))
    return [row[0] for row in rows]


# get service details (price, duration)
def get_stylist_services_details(first_name, last_name):
    query = """
    select sv.service_name, sv.duration, ss.price, if(sv.addOn, 'yes', 'no')
    from services sv
    join stylist_services ss on sv.service_id = ss.service_id
    join stylists st on ss.stylist_id = st.stylist_id
    where st.first_name = %s and st.last_name = %s
    order by sv.service_name
    """
    return run_select(query, (first_name, last_name))


# get reviews for a stylist
def get_stylist_reviews(first_name, last_name):
    query = """
    select r.rating, r.client_review, r.review_date
    from reviews r
    join appointments a on r.appointment_id = a.appointment_id
    join stylists st on a.stylist_id = st.stylist_id
    where st.first_name = %s and st.last_name = %s
    order by r.review_date desc
    """
    return run_select(query, (first_name, last_name))


# find client by phone
def get_client_by_phone(phone):
    rows = run_select('select client_id from clients where phone = %s', (phone,))
    return rows[0][0] if rows else None


# insert new client
def insert_client(first_name, last_name, phone, email):
    success, client_id = run_action(
        'insert into clients (first_name, last_name, phone, email) values (%s, %s, %s, %s)',
        (first_name, last_name, phone, email)
    )
    return client_id if success else None


# get ids for stylist and service
def get_stylist_service_ids(first_name, last_name, service_name):
    query = """
    select st.stylist_id, sv.service_id
    from stylists st
    join stylist_services ss on st.stylist_id = ss.stylist_id
    join services sv on ss.service_id = sv.service_id
    where st.first_name = %s and st.last_name = %s and sv.service_name = %s
    """
    rows = run_select(query, (first_name, last_name, service_name))
    return rows[0] if rows else None


# check if time slot already taken
def appointment_slot_taken(stylist_id, appt_date, appt_time, exclude_appointment_id=None):
    query = """
    select appointment_id
    from appointments
    where stylist_id = %s
      and appointment_date = %s
      and appointment_time = %s
      and appointment_status in ('scheduled', 'completed')
    """
    params = [stylist_id, appt_date, appt_time]

    if exclude_appointment_id is not None:
        query += ' and appointment_id <> %s'
        params.append(exclude_appointment_id)

    rows = run_select(query, tuple(params))
    return len(rows) > 0


# book appointment
def book_appointment_db(client_id, stylist_id, service_id, appt_date, appt_time):
    # check if slot taken
    if appointment_slot_taken(stylist_id, appt_date, appt_time):
        return False, 'that time is already booked for this stylist.'

    success, _ = run_action(
        """
        insert into appointments (client_id, stylist_id, service_id, appointment_date, appointment_time, appointment_status)
        values (%s, %s, %s, %s, %s, 'scheduled')
        """,
        (client_id, stylist_id, service_id, appt_date, appt_time)
    )

    if success:
        return True, 'appointment booked successfully.'
    return False, 'booking failed.'


# get all appointments for a client
def get_client_appointments(phone):
    query = """
    select
        a.appointment_id,
        concat(st.first_name, ' ', st.last_name) as stylist,
        sv.service_name,
        a.appointment_date,
        a.appointment_time,
        a.appointment_status,
        (
            select count(*)
            from appointments a2
            where a2.client_id = c.client_id and a2.stylist_id = st.stylist_id
        ) as count_with_stylist,
        (
            select count(*)
            from appointments a3
            where a3.client_id = c.client_id
        ) as total_client_appts
    from appointments a
    join clients c on a.client_id = c.client_id
    join stylists st on a.stylist_id = st.stylist_id
    join services sv on a.service_id = sv.service_id
    where c.phone = %s
    order by a.appointment_date desc, a.appointment_time desc
    """
    return run_select(query, (phone,))


# cancel appointment
def cancel_appointment_db(appointment_id):
    query = """
    update appointments
    set appointment_status = 'cancelled'
    where appointment_id = %s and appointment_status = 'scheduled'
    """
    success, _ = run_action(query, (appointment_id,))
    return success


# reschedule appointment
def reschedule_appointment_db(appointment_id, stylist_id, new_date, new_time):
    # check if new time is taken
    if appointment_slot_taken(stylist_id, new_date, new_time, exclude_appointment_id=appointment_id):
        return False, 'that new time is already booked for this stylist.'

    query = """
    update appointments
    set appointment_date = %s,
        appointment_time = %s
    where appointment_id = %s and appointment_status = 'scheduled'
    """
    success, _ = run_action(query, (new_date, new_time, appointment_id))

    if success:
        return True, 'appointment rescheduled.'
    return False, 'reschedule failed.'


# get completed appointments for review
def get_completed_appointments_for_review(phone):    
    query = """
    select a.appointment_id, concat(st.first_name, ' ', st.last_name), sv.service_name, a.appointment_date
    from appointments a
    join clients c on a.client_id = c.client_id
    join stylists st on a.stylist_id = st.stylist_id
    join services sv on a.service_id = sv.service_id
    left join reviews r on a.appointment_id = r.appointment_id
    where c.phone = %s and a.appointment_status = 'completed' and r.review_id is null
    order by a.appointment_date desc
    """
    return run_select(query, (phone,))


# insert a review
def insert_review(appointment_id, rating, review_text):
    success, _ = run_action(
        'insert into reviews (appointment_id, rating, client_review, review_date) values (%s, %s, %s, curdate())',
        (appointment_id, rating, review_text)
    )
    return success