from alembic import op

revision = 'e16be34af36b'
down_revision = 'f80162856884'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""

    CREATE OR REPLACE FUNCTION check_orders_game_fk()
    RETURNS TRIGGER AS $$
    DECLARE
      p_game INT;
      t_game INT;
    BEGIN
      SELECT game_id INTO p_game FROM nation WHERE id = NEW.player_id;
      SELECT game_id INTO t_game FROM turn   WHERE id = NEW.turn_id;

      IF p_game IS NULL OR t_game IS NULL OR p_game <> t_game THEN
        RAISE EXCEPTION 'Order player/turn game mismatch (player_id=%, turn_id=%)', NEW.player_id, NEW.turn_id
          USING ERRCODE = 'foreign_key_violation';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;


    DROP TRIGGER IF EXISTS trg_check_orders_game ON orders;


    CREATE TRIGGER trg_check_orders_game
      BEFORE INSERT OR UPDATE ON orders
      FOR EACH ROW
      EXECUTE FUNCTION check_orders_game_fk();
    """)


def downgrade():
    op.execute("""
    DROP TRIGGER IF EXISTS trg_check_orders_game ON orders;
    DROP FUNCTION IF EXISTS check_orders_game_fk();
    """)
