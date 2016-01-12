create table if not exists submissions (
  submitted_at timestamp default current_timestamp,
  lift_score real not null
);

create table if not exists actuals (
  Customer_ID integer,
  Churn integer
);
