def create_container(container_manager, challenge_id, user_id, team_id, docker_assignment):
    """
    Create a new container for a challenge.
    """
    log("containers_debug", format="CHALL_ID:{challenge_id}|Initiating container creation process",
            challenge_id=challenge_id)

    challenge = ContainerChallenge.challenge_model.query.filter_by(id=challenge_id).first()

    if challenge is None:
        log("containers_errors", format="CHALL_ID:{challenge_id}|Container creation failed (Challenge not found)",
                challenge_id=challenge_id)
        return {"error": "Challenge not found"}, 400

    # ... (keep existing checks) ...

    try:
        created_container = container_manager.create_container(
            challenge.image, 
            challenge.port_range_start,
            challenge.port_range_end,
            challenge.command, 
            challenge.volumes
        )
    except Exception as err:
        log("containers_errors", format="CHALL_ID:{challenge_id}|Container creation failed: {error}",
                challenge_id=challenge_id,
                error=str(err))
        return {"error": "Failed to create container"}, 500

    # Get all port mappings
    port_mappings = container_manager.get_container_ports(created_container.id)

    if not port_mappings:
        log("containers_errors", format="CHALL_ID:{challenge_id}|Could not get ports for container '{container_id}'",
                challenge_id=challenge_id,
                container_id=created_container.id)
        return {"error": "Could not get container ports"}, 500

    expires = int(time.time() + container_manager.expiration_seconds)

    new_container = ContainerInfoModel(
        container_id=created_container.id,
        challenge_id=challenge.id,
        user_id=user_id,
        team_id=team_id,
        ports=json.dumps(port_mappings),  # Store port mappings as JSON
        timestamp=int(time.time()),
        expires=expires
    )

    try:
        db.session.add(new_container)
        db.session.commit()
        log("containers_actions", format="CHALL_ID:{challenge_id}|Container '{container_id}' created and added to database",
                challenge_id=challenge_id,
                container_id=created_container.id)
    except Exception as db_err:
        log("containers_errors", format="CHALL_ID:{challenge_id}|Failed to add container '{container_id}' to database: {error}",
                challenge_id=challenge_id,
                container_id=created_container.id,
                error=str(db_err))
        return {"error": "Failed to save container information"}, 500

    log("containers_debug", format="CHALL_ID:{challenge_id}|Container '{container_id}' creation process completed",
            challenge_id=challenge_id, container_id=created_container.id)
    
    return json.dumps({
        "status": "created",
        "hostname": challenge.connection_info,
        "ports": port_mappings,
        "expires": expires
    })

# ... (keep rest of the file unchanged) ...
