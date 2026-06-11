<?php
/**
 * Seed Moodle with users, courses, enrollments, and completions from CSV exports.
 * Run inside the Moodle container:
 *   php /seed-scripts/moodle_seed.php
 */

define('CLI_SCRIPT', true);

require('/var/www/html/config.php');
require_once($CFG->libdir . '/clilib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->libdir . '/enrollib.php');
require_once($CFG->libdir . '/completionlib.php');

$datadir = getenv('SEED_DATA_DIR') ?: '/seed-data';
$defaultpassword = 'Student123!';

function read_csv(string $path): array
{
    $rows = [];
    if (!file_exists($path)) {
        mtrace("Missing file: $path");
        return $rows;
    }
    $handle = fopen($path, 'r');
    $header = fgetcsv($handle);
    while (($data = fgetcsv($handle)) !== false) {
        if (count($data) === count($header)) {
            $rows[] = array_combine($header, $data);
        }
    }
    fclose($handle);
    return $rows;
}

function get_or_create_category(string $name): int
{
    global $DB;
    $existing = $DB->get_record('course_categories', ['name' => $name]);
    if ($existing) {
        return (int) $existing->id;
    }
    $created = core_course_category::create([
        'name' => $name,
        'parent' => 0,
        'visible' => 1,
    ]);
    mtrace("Created category: $name");
    return (int) $created->id;
}

function get_student_role_id(): int
{
    global $DB;
    return (int) $DB->get_field('role', 'id', ['shortname' => 'student']);
}

mtrace('=== Moodle seed started ===');

$DB->get_manager(); // ensure DB ready
$studentroleid = get_student_role_id();
$manual = enrol_get_plugin('manual');

// Update site name for college project
$DB->set_field('config', 'value', 'SJSU Online Learning Demo', ['name' => 'fullname']);
$DB->set_field('config', 'value', 'SJSU Online Learning Demo', ['name' => 'shortname']);

$courses = read_csv("$datadir/mdl_course.csv");
$users = read_csv("$datadir/mdl_user.csv");
$enrolments = read_csv("$datadir/mdl_user_enrolments.csv");
$completions = read_csv("$datadir/mdl_course_completions.csv");
$enrolmeta = read_csv("$datadir/mdl_enrol.csv");

$courseidmap = [];   // csv course id -> moodle course id
$useridmap = [];     // csv user id -> moodle user id
$enrolidmap = [];    // csv enrol id -> moodle course id

// --- Courses ---
foreach ($courses as $row) {
    $shortname = $row['shortname'];
    $existing = $DB->get_record('course', ['shortname' => $shortname]);
    if ($existing) {
        $courseidmap[$row['id']] = (int) $existing->id;
        mtrace("Course exists: $shortname");
        continue;
    }

    $categoryid = get_or_create_category($row['category']);
    $course = new stdClass();
    $course->category = $categoryid;
    $course->fullname = $row['fullname'];
    $course->shortname = $shortname;
    $course->summary = 'Online course for the SJSU Data Visualization class project.';
    $course->summaryformat = FORMAT_HTML;
    $course->format = 'topics';
    $course->numsections = 3;
    $course->startdate = time();
    $course->visible = 1;
    $course->enablecompletion = 1;
    $course->showgrades = 1;

    $created = create_course($course);
    $courseidmap[$row['id']] = (int) $created->id;
    mtrace("Created course: {$row['fullname']}");

    // Ensure manual enrol instance exists
    $instance = $DB->get_record('enrol', ['courseid' => $created->id, 'enrol' => 'manual']);
    if (!$instance) {
        $manual->add_instance($created);
    }
}

foreach ($enrolmeta as $row) {
    $csvid = $row['courseid'];
    if (isset($courseidmap[$csvid])) {
        $enrolidmap[$row['id']] = $courseidmap[$csvid];
    }
}

// --- Users ---
$createdusers = 0;
foreach ($users as $row) {
    if (!empty($row['deleted'])) {
        continue;
    }
    $username = $row['username'];
    $existing = $DB->get_record('user', ['username' => $username, 'mnethostid' => $CFG->mnet_localhost_id]);
    if ($existing) {
        $useridmap[$row['id']] = (int) $existing->id;
        continue;
    }

    $user = new stdClass();
    $user->username = $username;
    $user->firstname = $row['firstname'];
    $user->lastname = $row['lastname'];
    $user->email = $row['email'];
    $user->department = $row['program'];
    $user->institution = 'San Jose State University';
    $user->city = 'San Jose';
    $user->country = 'US';
    $user->auth = 'manual';
    $user->password = $defaultpassword;
    $user->confirmed = 1;
    $user->mnethostid = $CFG->mnet_localhost_id;

    $newid = user_create_user($user, false, false);
    $useridmap[$row['id']] = (int) $newid;
    $createdusers++;
}
mtrace("Users ready: " . count($useridmap) . " (new: $createdusers)");

// --- Enrollments ---
$enrolled = 0;
foreach ($enrolments as $row) {
    $csvuserid = $row['userid'];
    $csvenrolid = $row['enrolid'];
    if (!isset($useridmap[$csvuserid], $enrolidmap[$csvenrolid])) {
        continue;
    }
    $userid = $useridmap[$csvuserid];
    $courseid = $enrolidmap[$csvenrolid];

    $instance = $DB->get_record('enrol', ['courseid' => $courseid, 'enrol' => 'manual'], '*', IGNORE_MULTIPLE);
    if (!$instance) {
        $course = get_course($courseid);
        $manual->add_instance($course);
        $instance = $DB->get_record('enrol', ['courseid' => $courseid, 'enrol' => 'manual'], '*', IGNORE_MULTIPLE);
    }

    if (!$DB->record_exists('user_enrolments', ['userid' => $userid, 'enrolid' => $instance->id])) {
        $manual->enrol_user($instance, $userid, $studentroleid);
        $enrolled++;
    }
}
mtrace("Enrollments created: $enrolled");

// --- Completions ---
$completed = 0;
foreach ($completions as $row) {
    $csvuserid = $row['userid'];
    $csvcourseid = $row['course'];
    if (!isset($useridmap[$csvuserid], $courseidmap[$csvcourseid])) {
        continue;
    }
    $userid = $useridmap[$csvuserid];
    $courseid = $courseidmap[$csvcourseid];
    $timeenrolled = (int) $row['timeenrolled'];
    $timecompleted = $row['timecompleted'] !== '' && $row['timecompleted'] !== null
        ? (int) $row['timecompleted']
        : 0;

    $existing = $DB->get_record('course_completions', ['userid' => $userid, 'course' => $courseid]);
    if ($existing) {
        if ($timecompleted > 0 && empty($existing->timecompleted)) {
            $existing->timecompleted = $timecompleted;
            $DB->update_record('course_completions', $existing);
            $completed++;
        }
        continue;
    }

    $record = new stdClass();
    $record->userid = $userid;
    $record->course = $courseid;
    $record->timeenrolled = $timeenrolled ?: time();
    $record->timecompleted = $timecompleted > 0 ? $timecompleted : null;
    $record->reaggregate = 0;
    $DB->insert_record('course_completions', $record);
    if ($timecompleted > 0) {
        $completed++;
    }
}
mtrace("Completion records: $completed with finish dates");

mtrace('=== Moodle seed complete ===');
mtrace('Login as any student: username from CSV / password: ' . $defaultpassword);
mtrace('Admin: admin / Admin123!');
