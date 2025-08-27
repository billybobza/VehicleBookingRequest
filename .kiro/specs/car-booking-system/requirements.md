# Requirements Document

## Introduction

The car booking system is a web application that allows office employees to request and book usage of company vehicles. The system will manage vehicle availability, booking requests, and automatically calculate return dates based on business rules. The frontend will be built with Svelte 5, the backend with FastAPI (Python), and data will be stored in SQLite.

## Requirements

### Requirement 1

**User Story:** As an office employee, I want to view and select from available company vehicles, so that I can choose the most appropriate car for my needs.

#### Acceptance Criteria

1. WHEN the user accesses the booking page THEN the system SHALL display a dropdown list of vehicle registrations
2. WHEN displaying vehicle registrations THEN the system SHALL include the make and color of each vehicle
3. WHEN the system initializes THEN the system SHALL seed the database with 11 company vehicles
4. WHEN a vehicle is selected THEN the system SHALL show only vehicles that are available for the requested time period

### Requirement 2

**User Story:** As an office employee, I want to specify when I need the vehicle and for how long, so that the system can check availability and calculate return dates.

#### Acceptance Criteria

1. WHEN the user selects a booking date and time THEN the system SHALL validate the date is not in the past
2. WHEN the user selects duration THEN the system SHALL provide options including "1 hour", "2 days", "3 weeks" and other common durations
3. WHEN the user specifies duration THEN the system SHALL automatically calculate the return date and time
4. WHEN the last usage day falls on a Friday THEN the system SHALL set the return date to Monday morning
5. WHEN the last usage day falls on a weekend THEN the system SHALL set the return date to the next Monday morning

### Requirement 3

**User Story:** As an office employee, I want to provide the reason for vehicle usage and estimated mileage, so that the company can track vehicle usage patterns and maintenance needs.

#### Acceptance Criteria

1. WHEN submitting a booking request THEN the system SHALL require a reason for usage
2. WHEN submitting a booking request THEN the system SHALL require an estimated mileage value
3. WHEN the user enters estimated mileage THEN the system SHALL validate it is a positive number
4. WHEN the reason field is empty THEN the system SHALL display a validation error

### Requirement 4

**User Story:** As a system administrator, I want the system to track vehicle availability automatically, so that double bookings are prevented and accurate availability is shown to users.

#### Acceptance Criteria

1. WHEN the system initializes THEN the system SHALL seed random availability data for all vehicles for the next 3 months
2. WHEN a booking is confirmed THEN the system SHALL mark the vehicle as unavailable for the booked time period
3. WHEN checking availability THEN the system SHALL only show vehicles that are free for the entire requested duration
4. WHEN a vehicle is returned THEN the system SHALL mark the vehicle as available again

### Requirement 5

**User Story:** As an office employee, I want to submit my booking request through an intuitive interface, so that I can quickly and easily reserve a vehicle.

#### Acceptance Criteria

1. WHEN the user accesses the application THEN the system SHALL display the booking request form as the landing page
2. WHEN all required fields are completed THEN the system SHALL enable the submit button
3. WHEN the form is submitted with valid data THEN the system SHALL create the booking and display a confirmation
4. WHEN the form is submitted with invalid data THEN the system SHALL display appropriate error messages
5. WHEN the booking is successful THEN the system SHALL provide booking details including confirmation number

### Requirement 6

**User Story:** As a system, I want to maintain data persistence and integrity, so that booking information is reliably stored and retrieved.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL connect to the SQLite database
2. WHEN database tables don't exist THEN the system SHALL create the required schema
3. WHEN storing booking data THEN the system SHALL ensure all required fields are persisted
4. WHEN retrieving availability data THEN the system SHALL return accurate real-time information
5. WHEN the system encounters database errors THEN the system SHALL log errors and display user-friendly messages